from typing import Any

from moduls_to_calculate.carbon_values import CarbonSegment
from moduls_to_calculate.classes_for_additional_plate import AdditionConcrete
from moduls_to_calculate.classes_for_concrete_segment_and_steel import ElementOfSection, AConcreteSection, ASteelLine
from moduls_to_calculate.modul_to_calculate import calculate_result
from variables.variables_for_material import MaterialVariables
from moduls_to_calculate.diagram import DiagramConcrete, DiagramToDraw, Diagram
from PySide6.QtGui import QColor
from variables.variables_the_program import MyColors, InitiationValues


class AllElementsOfTheSection:
    n_points_for_graph = 40

    def __init__(self, concrete_class: str = InitiationValues.default_concrete_class,
                 type_of_diagram_steel: int = 0, type_of_diagram_concrete: int = 0, n: int = InitiationValues.n,
                 normal_force: float = InitiationValues.normal_force,
                 eccentricity: float = InitiationValues.eccentricity,
                 dn: float = InitiationValues.d_n):
        self._list_of_concrete_sections: list[AConcreteSection | ElementOfSection] = [AConcreteSection()]
        self._list_of_steel: list[ASteelLine | ElementOfSection] = [ASteelLine()]
        self._concrete_class: str = concrete_class
        self._concrete_diagram = DiagramConcrete(concrete_class=concrete_class)
        self._type_of_diagram_steel = 0
        self.type_of_diagram_concrete = 0
        self._concrete_color_rgba = MyColors.concrete_diagram
        self._n = n  # the smallest part will be divided into n elements
        self._normal_force = normal_force  # + compression - tension
        self._dn = dn
        self._n_de = InitiationValues.d_e
        self.is_calculated = False
        self._result = dict()
        self._eccentricity = eccentricity
        self.carbon = CarbonSegment()
        self.addition_concrete = AdditionConcrete()

    @property
    def eccentricity(self):
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, new_value: float):
        self._eccentricity = new_value

    @property
    def type_of_diagram_steel(self) -> int:
        return self._type_of_diagram_steel

    @type_of_diagram_steel.setter
    def type_of_diagram_steel(self, new_type: int):
        self._type_of_diagram_steel = new_type
        for steel_line in self._list_of_steel:
            steel_line.update_s0(type_of_diagram=new_type)

    def get_prestressed_force(self) -> float:
        prestressed_force = 0
        for steel_line in self._list_of_steel:
            prestressed_force += steel_line.get_prestressed_force()
        return prestressed_force

    @property
    def list_of_concrete_sections(self):
        return self._list_of_concrete_sections

    @list_of_concrete_sections.setter
    def list_of_concrete_sections(self, new_list: list[AConcreteSection]):
        self._list_of_concrete_sections = new_list
        self.correct_new_concrete_section()

    @property
    def result(self):
        return self._result

    @property
    def n_de(self):
        return self._n_de

    @n_de.setter
    def n_de(self, new_value):
        self._n_de = new_value
        self.is_calculated = False

    def recalculate(self) -> bool:
        """send dates to general function to calculate"""
        h = self.get_b_h_max()[1]
        y_min, es_at_bottom = self.get_es_at_the_bottom()
        eo_max = self._concrete_diagram.get_max_x_y(typ_of_diagram=self.type_of_diagram_concrete)[0]
        self._result = calculate_result(e_top_max=eo_max, e_bottom_max=es_at_bottom, h=h, y_min=y_min,
                                        n_de=self._n_de,
                                        normal_force=self._normal_force, e0=self._eccentricity,
                                        list_of_concrete_sections=self._list_of_concrete_sections,
                                        list_of_steel=self._list_of_steel, concrete_diagram=self._concrete_diagram,
                                        type_of_diagram_concrete=self.type_of_diagram_concrete,
                                        type_of_diagram_steel=self.type_of_diagram_steel,
                                        dn_max=self._dn, carbon=self.carbon, m_init=self.carbon.m_int,
                                        calculate_with_carbon=self.carbon.calculate_with_carbon,
                                        additional_plate=self.addition_concrete)
        return True if len(self._result) > 0 else False

    def get_es_at_the_bottom(self) -> tuple[float, float]:
        """the function returns es max for steel line at bottom"""
        line_of_steel_0 = self._list_of_steel[0]
        y_min = line_of_steel_0.get_d_y_n_m_steel_s0()[1]
        e_under = line_of_steel_0.steel.es_max
        for line_steel in self._list_of_steel:
            if y_min > line_steel.get_d_y_n_m_steel_s0()[1]:
                y_min = line_steel.get_d_y_n_m_steel_s0()[1]
                e_under = line_steel.steel.es_max
        return y_min, e_under

    @property
    def dn(self):
        return self._dn

    @dn.setter
    def dn(self, new_value: float):
        self._dn = new_value
        self.is_calculated = False

    @property
    def normal_force(self):
        return self._normal_force

    @normal_force.setter
    def normal_force(self, new_value: float):
        self._normal_force = new_value
        self.is_calculated = False

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, new_value: int):
        self._n = new_value
        self.is_calculated = False
        self.divide_all_concrete_sections()

    def divide_all_concrete_sections(self):
        h_min = 0
        for section in self._list_of_concrete_sections:
            h_i = section.h
            if h_i < h_min or h_min == 0:
                h_min = h_i
        dn = h_min / self._n
        for section in self._list_of_concrete_sections:
            section.divide_the_section(dn=dn)
        self.addition_concrete.section.divide_the_section(dn=dn)

    @property
    def concrete_important_coordinate(self) -> None | tuple[list[float], list[float | Any]] | tuple[
        list[float], list[float]]:
        return self._concrete_diagram.important_coordinate(typ_of_diagram=self.type_of_diagram_concrete)

    def add_an_element(self, new_element: ElementOfSection):
        if isinstance(new_element, AConcreteSection):
            # it is concrete
            self._list_of_concrete_sections.append(new_element)
            self.correct_new_concrete_section()
            self.is_calculated = False
            return self._list_of_concrete_sections[-1]
        else:
            # it is steel
            self._list_of_steel.append(new_element)
            self.is_calculated = False
            return self._list_of_steel[-1]

    @property
    def max_x_y_for_concrete(self) -> tuple[float, float]:
        return self._concrete_diagram.get_max_x_y(typ_of_diagram=self.type_of_diagram_concrete)

    @property
    def max_x_y_for_steel(self) -> tuple[float, float]:
        if self.carbon.calculate_with_carbon:
            max_x, max_y = self.carbon.carbon_diagram.get_max_x_y()
        else:
            max_x = max_y = 0
        for steel_line in self._list_of_steel:
            max_xi, max_yi = steel_line.steel.get_max_x_y()
            if max_xi > max_x:
                max_x = max_xi
            if max_yi > max_y:
                max_y = max_yi
        return max_x, max_y

    @property
    def concrete_class(self):
        return self._concrete_class

    @concrete_class.setter
    def concrete_class(self, new_class: str):
        self._concrete_class = new_class
        self._concrete_diagram = DiagramConcrete(concrete_class=new_class)
        for concrete_section in self._list_of_concrete_sections:
            concrete_section.concrete = new_class

    def remove_last_element(self, type_of_section: str):
        if type_of_section == MaterialVariables.concrete:
            if len(self._list_of_concrete_sections) == 1:
                return None
            else:
                self._list_of_concrete_sections.pop()
                self.correct_new_concrete_section()
        else:
            if len(self._list_of_steel) == 1:
                return None
            else:
                self._list_of_steel.pop()
        self.is_calculated = False
        return None

    def add_copy_of_last_element_and_return_it(self, type_of_section):
        if type_of_section == MaterialVariables.concrete:
            # it is concrete
            new_element = self._list_of_concrete_sections[-1].get_copy_of_me()
        else:
            # it is steel
            new_element = self._list_of_steel[-1].get_copy_of_me()
        new_element = self.add_an_element(new_element=new_element)
        return new_element

    def change_an_element(self, new_element: ElementOfSection, n: int):
        """the function get a new element and number in the list"""
        if isinstance(new_element, AConcreteSection):
            # it is concrete
            self._list_of_concrete_sections.remove(new_element)
            self.correct_new_concrete_section()
        else:
            # it is steel
            self._list_of_steel.remove(new_element)
        self.is_calculated = False

    def correct_new_concrete_section(self):
        yi = 0
        for a_section in self._list_of_concrete_sections:
            bo, bu, y0, h = a_section.get_bo_bu_y0_h()
            yi = a_section.correct_y_by_add_a_new_element_return_y_i_plus_1(yi=yi)
        bo, bu, y0, h = self._list_of_concrete_sections[-1].get_bo_bu_y0_h()
        self.addition_concrete.steel.h = h + y0
        self.divide_all_concrete_sections()
        self.is_calculated = False

    def get_b_h_max(self) -> tuple[float, float]:
        b = 0
        for section in self._list_of_concrete_sections:
            bo, bu, y0, h = section.get_bo_bu_y0_h()
            b = max(b, bo, bu)
        if self.addition_concrete.calculate_with_top_plate:
            b = max(b, self.addition_concrete.b)
        bo, bu, y0, h = self._list_of_concrete_sections[-1].get_bo_bu_y0_h()
        h += y0
        return b, h

    @property
    def list_of_steel(self):
        return self._list_of_steel

    @list_of_steel.setter
    def list_of_steel(self, new_list_of_steel: list[ASteelLine]):
        self._list_of_steel = new_list_of_steel

    def get_b_for_y(self, y: float):
        for section in self._list_of_concrete_sections:
            if section.y0 <= y <= section.y0 + section.h:
                return section.get_b_for_y(y=y)
            return self._list_of_concrete_sections[0].bo

    def get_b_bottom(self):
        return self._list_of_concrete_sections[0].bo

    def get_graph_for_concrete(self) -> DiagramToDraw:
        return get_graph(diagram=self._concrete_diagram,
                         n=AllElementsOfTheSection.n_points_for_graph,
                         typ_of_diagram=self.type_of_diagram_concrete,
                         color=self._concrete_color_rgba)

    def get_graph_for_steel(self) -> list[DiagramToDraw]:
        list_of_graph = []
        for steel_line in self._list_of_steel:
            list_of_graph.append(get_graph(diagram=steel_line.steel,
                                           n=AllElementsOfTheSection.n_points_for_graph,
                                           typ_of_diagram=self.type_of_diagram_steel,
                                           color=steel_line.color_QColor))
        return list_of_graph

    def get_graph_for_carbon(self) -> DiagramToDraw:
        return get_graph(diagram=self.carbon.carbon_diagram,
                         n=AllElementsOfTheSection.n_points_for_graph,
                         typ_of_diagram=self.type_of_diagram_steel,
                         color=MyColors.carbon_stress)


def get_graph(color: QColor, diagram: Diagram, n: int = 20, typ_of_diagram: int = 0) -> DiagramToDraw:
    """the function returns dates for diagram canvas"""
    max_x = diagram.get_max_x_y(typ_of_diagram=typ_of_diagram)[0]
    d_x = max_x / n
    coordinates = []
    x_i = 0
    while x_i <= max_x:
        y_i = diagram.get_stress(ec=x_i, typ_of_diagram=typ_of_diagram)
        coordinates.append([x_i, y_i])
        x_i += d_x
    important_coordinate = diagram.important_coordinate(typ_of_diagram=typ_of_diagram)
    return DiagramToDraw(coordinates=coordinates,
                         important_coordinate=important_coordinate,
                         color=color)
