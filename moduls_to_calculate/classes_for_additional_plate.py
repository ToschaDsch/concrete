import math

from moduls_to_calculate.classes_for_concrete_segment_and_steel import ASteelLine, AConcreteSection
from moduls_to_calculate.diagram import DiagramSteel, DiagramConcrete
from variables.variables_the_program import InitiationValues, MyColors


class SteelForAdditionPlate:
    def __init__(self):
        self._area = math.pi*((0.8*0.5)**2)*8
        self.steel_name = InitiationValues.default_steel_class
        self.steel_diagram = DiagramSteel(steel_type=self.steel_name)
        self._z = 10
        self.color = MyColors.steel_additional_plate
        d, m, n = self.get_d_m_n_from_area(area=self._area)
        self._h = 40  # to top of the section + additional plate
        y = self._h - self._z
        self.steel_line =ASteelLine(d=d, m=m, n=n, steel=self.steel_name, y=y)


    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, value):
        self._h = value
        y = self._h - self._z
        self.steel_line._y = y

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value
        y = self._h - self._z
        self.steel_line._y = y

    @staticmethod
    def get_d_m_n_from_area(area: float) -> tuple:
        m = 1
        n = 1
        d = 20*((area / (m*n*math.pi)) ** 0.5)
        return d, m, n

    @property
    def area(self) -> float:
        return self._area

    @area.setter
    def area(self, area: float):
        self._area = area
        d, m, n = self.get_d_m_n_from_area(area=area)
        self.steel_line.d = d


class AdditionConcrete:
    def __init__(self, concrete_class: str = InitiationValues.default_concrete_class,
                 h: float = InitiationValues.h_add, b: float = InitiationValues.b_add):
        self._concrete_class: str = concrete_class
        self._concrete_diagram = DiagramConcrete(concrete_class=concrete_class)
        self._calculate_with_top_plate: bool = False
        self.type_of_diagram_concrete = 0
        self._h = h
        self._b = b
        self.section = AConcreteSection(bo=self.b, bu=self.b, h=self.h, concrete_class=self.concrete_class)
        self.steel = SteelForAdditionPlate()
        self.m_int = 0

    @property
    def steel_name(self) -> str:
        return self.steel.steel_name

    @steel_name.setter
    def steel_name(self, steel_name: str):
        self.steel.steel_diagram = DiagramSteel(steel_type=steel_name)


    @property
    def b(self) -> float:
        return self._b

    @b.setter
    def b(self, value: float):
        self._b = value
        bo, bu, y0, h = self.section.get_bo_bu_y0_h()
        self.section.new_bo_bu_y0_h(bo=self._b, bu=self._b, y0=y0, h=h)

    @property
    def h(self) -> float:
        return self._h

    @h.setter
    def h(self, value: float):
        self._h = value
        bo, bu, y0, h = self.section.get_bo_bu_y0_h()
        self.section.new_bo_bu_y0_h(bo=bo, bu=bu, y0=y0, h=self._h)
        self.steel.h = value + y0

    @property
    def calculate_with_top_plate(self):
        return self._calculate_with_top_plate

    @calculate_with_top_plate.setter
    def calculate_with_top_plate(self, new_value: bool):
        self._calculate_with_top_plate = new_value

    @property
    def concrete_class(self):
        return self._concrete_class

    @concrete_class.setter
    def concrete_class(self, new_class: str):
        self._concrete_class = new_class
        self._concrete_diagram = DiagramConcrete(concrete_class=new_class)
