from collections import defaultdict
from ssl import DER_cert_to_PEM_cert
from typing import Any

from moduls_to_calculate.carbon_values import CarbonSegment
from moduls_to_calculate.classes_for_additional_plate import AdditionConcrete
from moduls_to_calculate.classes_for_concrete_segment_and_steel import AConcreteSection, ASteelLine
from moduls_to_calculate.diagram import DiagramConcrete
from variables.variables_for_material import Result, GeneralGraphicForResult, ResultGraphSteel
from variables.variables_the_program import Menus


class NoneResult:
    def __init__(self, cause: str = 'default'):
        self._cause = cause

    def __str__(self) -> str:
        return self._cause


class CalculateWithCarbon:
    def __init__(self, calculate_with_carbon, m_init, carbon):
        self.calculate_with_carbon = calculate_with_carbon
        self.m_init = m_init
        self.carbon: CarbonSegment = carbon


class CalculateData:
    """
    :param dn_max: max difference between normal force in the section and calculated normal force - max error
    :param type_of_diagram_steel:
    :param type_of_diagram_concrete:
    :param concrete_diagram:
    :param list_of_steel:
    :param list_of_concrete_sections:
    :param h: height of the section, cm
    :param normal_force: kN
    """

    def __init__(self, dn_max: float, type_of_diagram_concrete: int, type_of_diagram_steel: int,
                 concrete_diagram: DiagramConcrete, normal_force: float, e0: float,
                 h: float, list_of_concrete_sections: list[AConcreteSection], list_of_steel: list[ASteelLine],
                 calculate_with_carbon, calculate_with_additional_plate: bool, addition_plate):
        self.dn_max = dn_max
        self.normal_force = normal_force
        self.type_of_diagram_concrete = type_of_diagram_concrete
        self.type_of_diagram_steel = type_of_diagram_steel
        self.h = h
        self.concrete_diagram = concrete_diagram
        self.list_of_concrete_sections = list_of_concrete_sections
        self.list_of_steel = list_of_steel
        self.e0 = e0
        self.calculate_with_carbon: CalculateWithCarbon = calculate_with_carbon
        self.calculate_with_additional_plate: bool = calculate_with_additional_plate
        self.additional_plate = addition_plate


def calculate_result(e_top_max: float, e_bottom_max: float, h: float, y_min: float, n_de: int,
                     normal_force: float, e0: float, list_of_concrete_sections: list[AConcreteSection],
                     list_of_steel: list[ASteelLine],
                     concrete_diagram: DiagramConcrete,
                     type_of_diagram_concrete: int,
                     type_of_diagram_steel: int, dn_max: float,
                     calculate_with_carbon=False,
                     m_init=0, carbon: CarbonSegment = None,
                     additional_plate = None) -> defaultdict:
    """
    the function makes iterations for deformations at the top of the section
    it finds deformations at the bottom for each iteration.
    and it  calculates moment and normal forces for these deformations

    :param additional_plate: a late at the section, it works after m > m_int
    :param carbon: segment of the carbon
    :param m_init: the section works by the moment with the carbon
    :param calculate_with_carbon: bool
    :param dn_max: max difference between normal force in the section and calculated normal force - max error
    :param type_of_diagram_steel:
    :param type_of_diagram_concrete:
    :param concrete_diagram:
    :param list_of_steel:
    :param list_of_concrete_sections:
    :param e_top_max:  limits of the deformation on the top of the general concrete section
    :param e_bottom_max:    limit of the deformation at the bottom of the general concrete section
    :param h: height of the section, cm
    :param y_min:   distance between the bottom of the section and the lower layer of reinforcement, cm
    :param n_de:    initial splitting of the deformation into segments
    :param normal_force: kN     strain is positive
    :param e0: m   eccentricity for normal force
    :return:    dict of classes Result for each moment
    """
    if carbon.calculate_with_carbon:
        carbon.m_1 = 0
        carbon.e_init = 0
    normal_force, e0 = correct_normal_force_with_prestress(normal_force=normal_force, e0=e0,
                                                           list_of_steel=list_of_steel)

    calculate_with_carbon = CalculateWithCarbon(calculate_with_carbon=calculate_with_carbon,
                                                m_init=m_init, carbon=carbon)
    calculate_date = CalculateData(dn_max=dn_max, type_of_diagram_concrete=type_of_diagram_concrete,
                                   type_of_diagram_steel=type_of_diagram_steel, concrete_diagram=concrete_diagram,
                                   normal_force=normal_force, e0=e0, h=h,
                                   list_of_concrete_sections=list_of_concrete_sections, list_of_steel=list_of_steel,
                                   calculate_with_carbon=calculate_with_carbon,
                                   calculate_with_additional_plate=additional_plate.calculate_with_top_plate,
                                   addition_plate=additional_plate)
    n_de = int(n_de)
    if carbon.calculate_with_carbon and m_init > 0:
        result = calculation_with_carbon(carbon=carbon, calculate_date=calculate_date, m_init=m_init, n_de=n_de,
                                         e_bottom_max=e_bottom_max, e_top_max=e_top_max, y_min=y_min, h=h)
    elif additional_plate.calculate_with_top_plate:
        result = calculation_with_addiction_plate(additional_plate=additional_plate, calculate_date=calculate_date,
                                                m_init=additional_plate.m_int, n_de=n_de,
                                                e_bottom_max=e_bottom_max, e_top_max=e_top_max, y_min=y_min, h=h)
    else:
        result = normal_calculation(n_de=n_de, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                    calculate_date=calculate_date, e_top_max=e_top_max)

    result = check_the_result(result=result, dn_max=dn_max)
    return result

def check_the_result(result: defaultdict, dn_max: float) -> defaultdict:
    """the function deletes laa results with normal force > dn_max"""
    new_dict = defaultdict()
    for key, value in result.items():
        if abs(value.dn) <= dn_max:
            new_dict[key] = value
    return new_dict


def normal_calculation(n_de: int, e_top_max: float, e_bottom_max: float, h: float, y_min: float,
                       calculate_date: CalculateData, e_top_reinforcement: float=None) -> defaultdict:
    """the function calculate a range for top displacement and find a result for all nu,bers"""
    result = defaultdict()
    if e_top_reinforcement is None:
        n_0 = 0
    else:
        if calculate_date.calculate_with_additional_plate:
            h += calculate_date.additional_plate.h
            calculate_date.h = h
            n_0 = 0     #2*int(0.8*e_top_reinforcement/e_top_max*n_de) # not calculate from null
        else:
            n_0 = 0

    for i in range(n_0, n_de):
        e_top_i = e_top_max * i / n_de
        result_i = find_eo_and_get_result(e_top_i=e_top_i, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                          calculate_date=calculate_date, n_de=n_de)
        if result_i is None or result_i.moment < 0:
            continue
        result[result_i.moment] = result_i
    return result

def calculation_with_addiction_plate(additional_plate, calculate_date: CalculateData,
                                     m_init: float, n_de: int,
                            e_bottom_max: float, h: float, y_min: float, e_top_max: float) -> defaultdict:
    """the function calculate the result with a plate at the top of the section
    after m > m_inf"""
    # calculation without carbon for e_init
    additional_plate.calculate_with_top_plate = False
    calculate_date.calculate_with_additional_plate = False
    result, result_1, result__1 = calculate_to_the_moment(calculate_date=calculate_date,
                                     m_init=m_init, n_de=n_de,
                            e_bottom_max=e_bottom_max, h=h, y_min=y_min, e_top_max=e_top_max)
    if result_1 is None:
        return result
    additional_plate.steel.steel_line.calculate_e_init_additional_plate(result__1=result__1, result_1=result_1, m_init=m_init, h=h)
    additional_plate.section.calculate_e_init_additional_plate(result__1=result__1, result_1=result_1, m_init=m_init, h=h)

    # calculation with the plate
    additional_plate.calculate_with_top_plate = True
    calculate_date.calculate_with_additional_plate = True
    result_add_plate = normal_calculation(n_de=n_de, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                          calculate_date=calculate_date, e_top_max=e_top_max, e_top_reinforcement=result_1.e_top)
    for m_i, result_i in result_add_plate.items():
        if m_i <= m_init:
            continue
        else:
            result[m_i] = result_i
    return result

def calculate_to_the_moment(m_init: float, n_de: int,
                            e_bottom_max: float, h: float, y_min: float, e_top_max: float,
                            calculate_date: CalculateData) -> tuple[defaultdict, None, None] | tuple[
    defaultdict[Any, Any], Any | None, Any | None]:
    """the function make normal calculation without addition plat and carbon
    until m < m_init
    and returns a dict with all results + a result with m < m_init, a result with m > m_init """
    result_0 = normal_calculation(n_de=n_de, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                  calculate_date=calculate_date, e_top_max=e_top_max)
    if list(result_0.keys())[-1] < m_init:
        return result_0, None, None
    result = defaultdict()
    result__1 = None
    result_1 = None
    for m_i, result_i in result_0.items():
        if m_i <= m_init:
            result[m_i] = result_i
            result__1 = result_i
        else:
            result_1 = result_i
            break
    return result, result_1, result__1

def calculation_with_carbon(carbon: CarbonSegment, calculate_date: CalculateData, m_init: float, n_de: int,
                            e_bottom_max: float, h: float, y_min: float, e_top_max: float, ) -> defaultdict:
    # calculation without carbon for e_init
    carbon.calculate_with_carbon = False
    calculate_date.calculate_with_carbon.carbon.calculate_with_carbon = False
    calculate_date.calculate_with_carbon.calculate_with_carbon = False
    result, result_1, result__1 = calculate_to_the_moment(calculate_date=calculate_date,
                                                          m_init=m_init, n_de=n_de,
                                                          e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                                          e_top_max=e_top_max)
    if result_1 is None:
        return result
    carbon.calculate_e_init(result__1=result__1, result_1=result_1, m_init=m_init, h=h)

    # calculation with the carbon
    carbon.calculate_with_carbon = True
    calculate_date.calculate_with_carbon.carbon.calculate_with_carbon = True
    calculate_date.calculate_with_carbon.calculate_with_carbon = True
    result_carbon = normal_calculation(n_de=n_de, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                       calculate_date=calculate_date, e_top_max=e_top_max)
    for m_i, result_i in result_carbon.items():
        if m_i <= m_init:
            continue
        else:
            result[m_i] = result_i
    return result


def correct_normal_force_with_prestress(normal_force: float, e0: float, list_of_steel: list[ASteelLine]) -> tuple[
    float, float]:
    if len(list_of_steel) == 0:
        return normal_force, e0
    moment = normal_force * e0
    for line_of_steel in list_of_steel:
        normal_force_i = line_of_steel.get_prestressed_force()  # kN
        y = line_of_steel.get_d_y_n_m_steel_s0()[1] / 100  # m
        moment += normal_force_i * y  # kNm
        normal_force += normal_force_i  # kN
    if normal_force == 0:
        return 0, 0
    return normal_force, moment / normal_force


def find_eo_and_get_result(e_top_i: float, e_bottom_max: float,
                           h: float, y_min: float,
                           calculate_date: CalculateData, n_de: int) -> Result:
    """
    the function find deformation at the top of the section (the lower reinforcement line)
    and calculate Result for the deformation
    :return: class Result for each moment
    """
    preliminary_list_eo_eu = make_a_list_with_preliminary_eo_eu(eo_i=e_top_i, eu_max=e_bottom_max,
                                                                h=h, y_min=y_min,
                                                                normal_force=calculate_date.normal_force,
                                                                n_de=n_de)
    result = find_e_bottom_for_e_top_get_result(preliminary_list_eo_eu=preliminary_list_eo_eu,
                                                calculate_date=calculate_date)
    return result


def make_a_list_with_preliminary_eo_eu(eo_i: float, eu_max: float,
                                       h: float, y_min: float,
                                       normal_force: float,
                                       n_de: int) -> list[list[float]]:
    """the function calculates a range for displacements at the bottom"""
    list_eo_eu = []  # eo - e_top, e_u - e bottom
    if normal_force < 0:
        eu_min = eu_max
        n = 2 * n_de
    else:
        eu_min = 0
        n = n_de
    for i in range(n):
        eu_s = - i / n_de * eu_max + eu_min
        eu = (eu_s - eo_i) / (h - y_min) * h + eo_i
        list_eo_eu.append([eo_i, eu])
    return list_eo_eu


def calculate_an_element(list_of_elements: list[ASteelLine|AConcreteSection], e_top: float, e_bottom: float, h: float,
                         type_of_diagram: int) -> tuple[int, int, list[Any], float, float] | None:
    """the function calculates a list of element
    concrete section os a line of steel
    :keyword"""
    normal_force = 0
    moment = 0
    graphic = []
    e_bottom_i, e_top_i = 0, 0
    for an_element in list_of_elements:
        result_i = an_element.get_n_m_graph(e_top=e_top, e_bottom=e_bottom, h=h,
                                                     type_of_diagram=type_of_diagram)
        if result_i is None:
            return None
        normal_force_i, moment_i, graphic_i, e_bottom_i, e_top_i = result_i
        normal_force += normal_force_i
        moment += moment_i
        graphic.append(graphic_i)
    return normal_force, moment, graphic, e_bottom_i, e_top_i

def get_m_n_from_eu_eo(e_top: float, e_bottom: float, h: float,
                       list_of_concrete_sections: list[AConcreteSection],
                       list_of_steel: list[ASteelLine],
                       type_of_diagram_concrete: int,
                       type_of_diagram_steel: int,
                       normal_force_0: float, e0: float,
                       concrete_diagram: DiagramConcrete,
                       calculate_with_carbon: bool = False,
                       carbon: CarbonSegment = None,
                       calculate_with_additional_plate: bool = False,
                       additional_plate=None) -> Result | NoneResult:
    # section without reinforcement
    result_normal_section = calculate_a_normal_section(e_top=e_top, e_bottom=e_bottom, h=h,
                                                       list_of_concrete_sections=list_of_concrete_sections,
                                                       list_of_steel=list_of_steel,
                                                       type_of_diagram_concrete=type_of_diagram_concrete,
                                                       type_of_diagram_steel=type_of_diagram_steel)
    if isinstance(result_normal_section, NoneResult):
        return result_normal_section
    normal_force_1, moment_1, graphic_concrete_1, graphic_steel_1 = result_normal_section

    # reinforcement with carbon
    result_carbon = calculate_carbon (e_top=e_top, e_bottom=e_bottom, h=h, carbon=carbon, calculate_with_carbon=calculate_with_carbon)
    if isinstance(result_carbon, NoneResult):
        return result_carbon
    normal_force_carbon, moment_carbon, graphic_carbon = result_carbon

    # reinforcement with an additional plate
    result_additional_plate = calculate_an_additional_plate(e_top=e_top, e_bottom=e_bottom, h=h,
                                                            additional_plate=additional_plate,
                                                            calculate_with_additional_plate=calculate_with_additional_plate,
                                                            type_of_diagram_concrete=type_of_diagram_concrete,
                                                            type_of_diagram_steel=type_of_diagram_steel)
    if isinstance(result_additional_plate, NoneResult):
        return result_additional_plate
    (normal_force_add_plate, moment_add_plate, graphic_concrete_2, graphic_steel_2,
     e_bottom_i_add_plate, e_top_i_add_plate) = result_additional_plate

    moment = normal_force_0 * e0 + moment_1 + moment_carbon + moment_add_plate # moment from the external normal
    normal_force = normal_force_1 + normal_force_carbon + normal_force_add_plate    # force kNm
    dn = normal_force_1  + normal_force_0 + normal_force_carbon + normal_force_add_plate # external normal force
    if len(graphic_concrete_2) > 0:
        graphic_concrete_1.append(graphic_concrete_2[0])

    graphic_steel = graphic_steel_1 + graphic_steel_2

    # strain is positive kN
    if e_top_i_add_plate:
        sc_add_plate = additional_plate.section.concrete.get_stress(ec=e_top_i_add_plate,
                                                            typ_of_diagram=type_of_diagram_concrete)
        #sc_add_plate = 12
        e_top = (e_top-e_bottom)/h*(h-additional_plate.section.h) + e_bottom
        e_top = 0 if e_top < 0 else e_top
    else:
        sc_add_plate = 0
    sc_general_section = concrete_diagram.get_stress(ec=e_top,
                                     typ_of_diagram=type_of_diagram_concrete)

    graphic = GeneralGraphicForResult(graphic_for_concrete=graphic_concrete_1,
                                      graphic_for_steel=graphic_steel,
                                      graphic_for_carbon=graphic_carbon)
    result = Result(normal_force=normal_force, moment=moment,
                    graph=graphic, e_bottom=e_bottom, e_top=e_top, dn=dn,
                    sc_general_section=sc_general_section, sc_addition_plate=sc_add_plate,
                    e_top_add_plate=e_top_i_add_plate, e_bottom_add_plate=e_bottom_i_add_plate)
    return result

def calculate_a_normal_section(e_top: float, e_bottom: float, h: float,
                       list_of_concrete_sections: list[AConcreteSection],
                       list_of_steel: list[ASteelLine],
                       type_of_diagram_concrete: int,
                       type_of_diagram_steel: int) -> NoneResult | tuple[int, int, list[Any], list[Any]]:
    """the function calculates a normal section without reinforcement
    (without carbon and an additional plate)"""

    # concrete
    result_concrete = calculate_an_element(
        list_of_elements=list_of_concrete_sections,
        e_top=e_top, e_bottom=e_bottom, h=h,
        type_of_diagram=type_of_diagram_concrete)
    if result_concrete is None:
        return NoneResult(cause='concrete')
    normal_force_concrete, moment_concrete, graphic_concrete, e_bottom_i, e_top_i = result_concrete
    # steel
    result_steel = calculate_an_element(
        list_of_elements=list_of_steel,
        e_top=e_top, e_bottom=e_bottom, h=h,
        type_of_diagram=type_of_diagram_steel)
    if result_steel is None:
        return NoneResult(cause='steel')
    normal_force_steel, moment_steel, graphic_steel, e_bottom_i, e_top_i = result_steel
    normal_force = normal_force_concrete + normal_force_steel
    moment = moment_concrete + moment_steel
    return normal_force, moment, graphic_concrete, graphic_steel

def calculate_carbon(e_top: float, e_bottom: float, h: float, carbon: CarbonSegment,
                     calculate_with_carbon: bool) -> NoneResult | tuple[
    float | int, float | int, ResultGraphSteel | Any]:
    """the function calculates a carbon reinforcement for the whole section"""
    if calculate_with_carbon:
        result_carbon = carbon.get_n_m_graph(e_top=e_top, e_bottom=e_bottom, h=h, type_of_diagram=0)
        if result_carbon is None:
            return NoneResult(cause='carbon')
        normal_force_carbon, moment_carbon, graphic_carbon = result_carbon
    else:
        normal_force_carbon, moment_carbon, graphic_carbon = 0, 0, carbon.get_null_graphic()
    return normal_force_carbon, moment_carbon, graphic_carbon

def calculate_an_additional_plate(e_top: float, e_bottom: float, h: float, calculate_with_additional_plate: bool,
                                  additional_plate: AdditionConcrete,
                                  type_of_diagram_concrete: int, type_of_diagram_steel: int)-> NoneResult | tuple[
                                                                        int, int, list[Any], list[Any], float, float]:
    """the function calculates an additional plate reinforcement for the whole section"""
    if calculate_with_additional_plate:
        # concrete
        result_concrete = calculate_an_element(
            list_of_elements=[additional_plate.section],
            e_top=e_top, e_bottom=e_bottom, h=h,
            type_of_diagram=type_of_diagram_concrete)
        if result_concrete is None:
            return NoneResult(cause='additional top plate, concrete')
        normal_force_concrete_2, moment_concrete_2, graphic_concrete_2, e_bottom_i, e_top_i = result_concrete
        # steel
        result_steel = calculate_an_element(
            list_of_elements=[additional_plate.steel.steel_line],
            e_top=e_top, e_bottom=e_bottom, h=h,
            type_of_diagram=type_of_diagram_steel)
        if result_steel is None:
            return NoneResult(cause='additional top plate, steel')
        normal_force_steel_2, moment_steel_2, graphic_steel_2, _, _ = result_steel
        normal_force_add_plate = normal_force_concrete_2 + normal_force_steel_2
        moment_add_plate = moment_concrete_2 + moment_steel_2
    else:
        normal_force_add_plate, moment_add_plate, e_bottom_i, e_top_i = 0,0,0,0
        graphic_concrete_2, graphic_steel_2 = [], []
    return normal_force_add_plate, moment_add_plate, graphic_concrete_2, graphic_steel_2, e_bottom_i, e_top_i

def find_precise_result_between_two_results(result_1: Result, result_2: Result, calculate_date: CalculateData,
                                            recursion: int = 0,
                                            additional_plate = None,
                                            calculate_with_additional_plate:bool = False) -> Result | None:
    """teh function checks two results and find new results between these with minimum dn"""

    if abs(result_1.dn) < calculate_date.dn_max:
        return result_1
    if abs(result_2.dn) < calculate_date.dn_max:
        return result_2
    eu_1 = result_1.e_bottom
    eu_2 = result_2.e_bottom
    dn_1 = result_1.dn
    dn_2 = result_2.dn
    if dn_1 - dn_2 == 0:
        print("can't find", result_1)
        return None
    else:
        e_bottom = (eu_2 - eu_1) / (dn_1 - dn_2) * dn_1 + eu_1
        e_top = result_1.e_top

    result = get_m_n_from_eu_eo(e_top=e_top, e_bottom=e_bottom, h=calculate_date.h,
                                list_of_concrete_sections=calculate_date.list_of_concrete_sections,
                                list_of_steel=calculate_date.list_of_steel,
                                normal_force_0=calculate_date.normal_force, e0=calculate_date.e0,
                                type_of_diagram_steel=calculate_date.type_of_diagram_steel,
                                type_of_diagram_concrete=calculate_date.type_of_diagram_concrete,
                                concrete_diagram=calculate_date.concrete_diagram,
                                carbon=calculate_date.calculate_with_carbon.carbon,
                                calculate_with_carbon=calculate_date.calculate_with_carbon.calculate_with_carbon,
                                calculate_with_additional_plate=calculate_with_additional_plate,
                                additional_plate=additional_plate)
    if isinstance(result, NoneResult) or recursion == Menus.max_recursion:
        if recursion == Menus.max_recursion:
            result = "recursion"
        print("can't find", result)
        return None

    if abs(result.dn) < calculate_date.dn_max:
        return result

    dn_result = result.dn

    if (dn_result < 0 < dn_1) or (dn_result > 0 > dn_1):
        result_2_ = result_1
    else:
        result_2_ = result_2

    recursion += 1
    return find_precise_result_between_two_results(result_1=result, result_2=result_2_, calculate_date=calculate_date,
                                                   recursion=recursion)


def check_primary_results_find_precise_e_top(results: list[Result], calculate_date: CalculateData
                                             ) -> Result | None:
    if len(results) == 0:
        return None
    elif len(results) == 1:
        return results[0]
    elif len(results) == 1:
        return find_precise_result_between_two_results(result_1=results[0], result_2=results[1],
                                                       calculate_date=calculate_date)
    if check_if_results_have_the_same_sign(results=results):
        return None
    min_dn1 = results[0].dn
    min_list_2_elements = [results[0], results[1]]
    # find two results with minimum
    for i, result_i in enumerate(results):
        if abs(result_i.dn) <= calculate_date.dn_max:
            return result_i
        if abs(result_i.dn) < min_dn1:
            min_dn1 = result_i.dn
            if i == 0:
                min_list_2_elements = [result_i, results[i + 1]]
            elif i == len(results) - 1:
                min_list_2_elements = [results[i - 1], result_i]
            else:
                if (result_i.dn >= 0 >= results[i + 1].dn) or (result_i.dn <= 0 <= results[i + 1].dn):
                    min_list_2_elements = [result_i, results[i + 1]]
                else:
                    min_list_2_elements = [results[i - 1], result_i]

    return find_precise_result_between_two_results(result_1=min_list_2_elements[0],
                                                   result_2=min_list_2_elements[1],
                                                   calculate_date=calculate_date)


def find_e_bottom_for_e_top_get_result(preliminary_list_eo_eu: list[list[float]],
                                       calculate_date: CalculateData) -> Result:
    list_or_preliminary_results = []
    n = 0

    for e_o, e_u in preliminary_list_eo_eu:
        result_i = get_m_n_from_eu_eo(e_top=e_o, e_bottom=e_u, h=calculate_date.h,
                                      normal_force_0=calculate_date.normal_force, e0=calculate_date.e0,
                                      list_of_concrete_sections=calculate_date.list_of_concrete_sections,
                                      list_of_steel=calculate_date.list_of_steel,
                                      concrete_diagram=calculate_date.concrete_diagram,
                                      type_of_diagram_concrete=calculate_date.type_of_diagram_concrete,
                                      type_of_diagram_steel=calculate_date.type_of_diagram_steel,
                                      carbon=calculate_date.calculate_with_carbon.carbon,
                                      calculate_with_carbon=calculate_date.calculate_with_carbon.calculate_with_carbon,
                                      calculate_with_additional_plate=calculate_date.calculate_with_additional_plate,
                                        additional_plate=calculate_date.additional_plate)
        n += 1
        if isinstance(result_i, NoneResult):
            #print('primary', result_i, n)
            continue
        list_or_preliminary_results.append(result_i)

    return check_primary_results_find_precise_e_top(results=list_or_preliminary_results, calculate_date=calculate_date)


def check_if_results_have_the_same_sign(results: list[Result]) -> bool:
    results_plus = len(list(filter(lambda x: (x.dn > 0), results)))
    results_minus = len(list(filter(lambda x: (x.dn < 0), results)))
    if len(results) == results_plus or len(results) == results_minus:  # there is no decision
        return False
    return False


