from collections import defaultdict

from moduls_to_calculate.carbon_values import CarbonSegment
from moduls_to_calculate.classes_for_concrete_segment_and_steel import AConcreteSection, ASteelLine
from moduls_to_calculate.diagram import DiagramConcrete
from variables.variables_for_material import Result, GeneralGraphicForResult, ResultGraphSteel
from variables.variables_the_program import Menus, InitiationValues, MyColors


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
                 h: float, list_of_concrete_sections: [AConcreteSection], list_of_steel: [ASteelLine],
                 calculate_with_carbon):
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


def calculate_result(e_top_max: float, e_bottom_max: float, h: float, y_min: float, n_de: int,
                     normal_force: float, e0: float, list_of_concrete_sections: [AConcreteSection],
                     list_of_steel: [ASteelLine],
                     concrete_diagram: DiagramConcrete,
                     type_of_diagram_concrete: int,
                     type_of_diagram_steel: int, dn_max: float,
                     calculate_with_carbon=False,
                     m_init=0, carbon: CarbonSegment = None) -> defaultdict:
    """
    the function makes iterations for deformations at the top of the section
    it finds deformations at the bottom for each iteration.
    and it  calculates moment and normal forces for these deformations

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
                                   calculate_with_carbon=calculate_with_carbon)
    n_de = int(n_de)
    if carbon.calculate_with_carbon and m_init > 0:
        result = calculation_with_carbon(carbon=carbon, calculate_date=calculate_date, m_init=m_init, n_de=n_de,
                                         e_bottom_max=e_bottom_max, e_top_max=e_top_max, y_min=y_min, h=h)
    else:
        result = normal_calculation(n_de=n_de, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                    calculate_date=calculate_date, e_top_max=e_top_max)
    return result


def normal_calculation(n_de: int, e_top_max: float, e_bottom_max: float, h: float, y_min: float,
                       calculate_date: CalculateData) -> defaultdict:
    result = defaultdict()
    for i in range(n_de):
        eo_i = e_top_max * i / n_de
        result_i = find_eo_and_get_result(e_top_i=eo_i, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                          calculate_date=calculate_date, n_de=n_de)
        if result_i is None:
            continue
        result[result_i.moment] = result_i
    return result


def calculation_with_carbon(carbon: CarbonSegment, calculate_date: CalculateData, m_init: float, n_de: int,
                            e_bottom_max: float, h: float, y_min: float, e_top_max: float, ) -> defaultdict:
    # calculation without carbon for e_init
    carbon.calculate_with_carbon = False
    calculate_date.calculate_with_carbon.carbon.calculate_with_carbon = False
    calculate_date.calculate_with_carbon.calculate_with_carbon = False
    result_0 = normal_calculation(n_de=n_de, e_bottom_max=e_bottom_max, h=h, y_min=y_min,
                                  calculate_date=calculate_date, e_top_max=e_top_max)
    if list(result_0.keys())[-1] < m_init:
        return result_0
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


def correct_normal_force_with_prestress(normal_force: float, e0: float, list_of_steel: [ASteelLine]) -> (float, float):
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
                                       n_de: int) -> [[float, float]]:
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


def calculate_concrete(list_of_concrete_sections: [AConcreteSection], e_top: float, e_bottom: float, h: float,
                       type_of_diagram_concrete: int) -> (list, list, list):
    normal_force = 0
    moment = 0
    graphic_concrete = []
    for concrete_section in list_of_concrete_sections:
        result_concrete_i = concrete_section.get_n_m_graph(e_top=e_top, e_bottom=e_bottom, h=h,
                                                           type_of_diagram=type_of_diagram_concrete)
        if result_concrete_i is None:
            return None
        normal_force_i, moment_i, graphic_i = result_concrete_i
        normal_force += normal_force_i
        moment += moment_i
        graphic_concrete.append(graphic_i)
    return normal_force, moment, graphic_concrete


def calculate_steel(list_of_steel: [ASteelLine], e_top: float, e_bottom: float, h: float,
                    type_of_diagram_steel: int) -> (list, list, list):
    graphic_steel = []
    normal_force_steel = 0
    moment_steel = 0
    for steel_section in list_of_steel:
        result_steel_i = steel_section.get_n_m_graph(e_top=e_top, e_bottom=e_bottom, h=h,
                                                     type_of_diagram=type_of_diagram_steel)
        if result_steel_i is None:
            return None
        normal_force_i, moment_i, graphic_i = result_steel_i
        normal_force_steel += normal_force_i
        moment_steel += moment_i
        graphic_steel.append(graphic_i)
    return normal_force_steel, moment_steel, graphic_steel


def get_m_n_from_eu_eo(e_top: float, e_bottom: float, h: float,
                       list_of_concrete_sections: [AConcreteSection],
                       list_of_steel: [ASteelLine],
                       type_of_diagram_concrete: int,
                       type_of_diagram_steel: int,
                       normal_force_0: float, e0: float,
                       concrete_diagram: DiagramConcrete,
                       calculate_with_carbon: bool = False,
                       carbon: CarbonSegment = None) -> Result | NoneResult:
    # concrete
    result_concrete = calculate_concrete(
        list_of_concrete_sections=list_of_concrete_sections,
        e_top=e_top, e_bottom=e_bottom, h=h,
        type_of_diagram_concrete=type_of_diagram_concrete)
    if result_concrete is None:
        return NoneResult(cause='concrete')
    normal_force_concrete, moment_concrete, graphic_concrete = result_concrete
    # steel
    result_steel = calculate_steel(
        list_of_steel=list_of_steel,
        e_top=e_top, e_bottom=e_bottom, h=h,
        type_of_diagram_steel=type_of_diagram_steel)
    if result_steel is None:
        return NoneResult(cause='steel')
    normal_force_steel, moment_steel, graphic_steel = result_steel
    # carbon
    if calculate_with_carbon:
        result_carbon = carbon.get_n_m_graph(e_top=e_top, e_bottom=e_bottom, h=h, type_of_diagram=0)
        if result_carbon is None:
            return NoneResult(cause='carbon')
        normal_force_carbon, moment_carbon, graphic_carbon = result_carbon
    else:
        normal_force_carbon, moment_carbon, graphic_carbon = 0, 0, carbon.get_null_graphic()
    moment = normal_force_0 * e0 + moment_steel + moment_concrete + moment_carbon  # moment from the external normal
    # force kNm
    normal_force = normal_force_concrete + normal_force_steel + normal_force_carbon
    dn = normal_force_concrete + normal_force_steel + normal_force_0 + normal_force_carbon  # external normal force
    # strain is positive kN
    sc = concrete_diagram.get_stress(ec=e_top,
                                     typ_of_diagram=type_of_diagram_concrete)

    graphic = GeneralGraphicForResult(graphic_for_concrete=graphic_concrete,
                                      graphic_for_steel=graphic_steel,
                                      graphic_for_carbon=graphic_carbon)
    result = Result(normal_force=normal_force, moment=moment, graph=graphic, eu=e_bottom, eo=e_top, dn=dn, sc=sc)
    return result


def find_precise_result_between_two_results(result_1: Result, result_2: Result, calculate_date: CalculateData,
                                            recursion: int = 0) -> Result | None:
    """teh function checks two results and find new results between these with minimum dn"""

    if abs(result_1.dn) < calculate_date.dn_max:
        return result_1
    if abs(result_2.dn) < calculate_date.dn_max:
        return result_2
    eu_1 = result_1.eu
    eu_2 = result_2.eu
    dn_1 = result_1.dn
    dn_2 = result_2.dn
    if dn_1 - dn_2 == 0:
        return result_1
    else:
        e_bottom = (eu_2 - eu_1) / (dn_1 - dn_2) * dn_1 + eu_1
        e_top = result_1.eo

    result = get_m_n_from_eu_eo(e_top=e_top, e_bottom=e_bottom, h=calculate_date.h,
                                list_of_concrete_sections=calculate_date.list_of_concrete_sections,
                                list_of_steel=calculate_date.list_of_steel,
                                normal_force_0=calculate_date.normal_force, e0=calculate_date.e0,
                                type_of_diagram_steel=calculate_date.type_of_diagram_steel,
                                type_of_diagram_concrete=calculate_date.type_of_diagram_concrete,
                                concrete_diagram=calculate_date.concrete_diagram,
                                carbon=calculate_date.calculate_with_carbon.carbon,
                                calculate_with_carbon=calculate_date.calculate_with_carbon.calculate_with_carbon)
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


def check_primary_results_find_precise_e_top(results: [Result], calculate_date: CalculateData
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


def find_e_bottom_for_e_top_get_result(preliminary_list_eo_eu: tuple[float, float],
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
                                      calculate_with_carbon=calculate_date.calculate_with_carbon.calculate_with_carbon
                                      )
        n += 1
        if isinstance(result_i, NoneResult):
            #print('primary', result_i, n)
            continue
        list_or_preliminary_results.append(result_i)

    return check_primary_results_find_precise_e_top(results=list_or_preliminary_results, calculate_date=calculate_date)


def check_if_results_have_the_same_sign(results: [Result]) -> bool:
    results_plus = len(list(filter(lambda x: (x.dn > 0), results)))
    results_minus = len(list(filter(lambda x: (x.dn < 0), results)))
    if len(results) == results_plus or len(results) == results_minus:  # there is no decision
        return False
    return False
