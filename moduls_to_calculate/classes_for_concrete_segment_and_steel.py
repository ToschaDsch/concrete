import math
import random
from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtGui import QColor

from moduls_to_calculate.carbon_diagramm import DiagramCarbon
from moduls_to_calculate.functions import get_ei_from_eo_eu_z_h
from moduls_to_calculate.diagram import DiagramConcrete, DiagramSteel
from variables.variables_for_material import ResultGraphConcrete, ResultGraphSteel, MaterialVariables, Result
from variables.variables_the_program import InitiationValues


class ElementOfSection(ABC):
    @abstractmethod
    def get_n_m_graph(self, e_top: float, e_bottom: float, h: float, type_of_diagram: int) -> tuple[float, float]:
        """the function returns normal force and moment relative of bottom of the section
                        + list for graphic with yi, stress"""
        pass

    @abstractmethod
    def get_copy_of_me(self):
        pass


class AConcreteSection(ElementOfSection):
    def __init__(self, bo: float = 10, bu: float = 10, y0: float = 0, h: float = 20,
                 concrete_class: str = InitiationValues.default_concrete_class):
        self._bo = bo
        self._bu = bu
        self._y0 = y0
        self._h = h
        self._concrete = DiagramConcrete(concrete_class=concrete_class)
        self._n = InitiationValues.n

    def divide_the_section(self, dn: float):
        if dn == 0:
            return None
        self._n = round(self._h / dn)
        return None

    @property
    def concrete(self):
        return self._concrete

    @concrete.setter
    def concrete(self, new_class: str):
        self._concrete = DiagramConcrete(concrete_class=new_class)

    def get_bo_bu_y0_h(self):
        return self._bo, self._bu, self._y0, self._h

    def new_bo_bu_y0_h(self, bo: float, bu: float, y0: float, h: float):
        self._bo = bo
        self._bu = bu
        self._y0 = y0
        self._h = h

    def correct_y_by_add_a_new_element_return_y_i_plus_1(self, yi: float) -> float:
        self._y0 = yi
        return self._y0 + self._h

    @property
    def bo(self) -> float:
        return self._bo

    @property
    def y0(self) -> float:
        return self._y0

    @y0.setter
    def y0(self, new_value: float):
        self._y0 = new_value

    @property
    def h(self) -> float:
        return self._h

    def get_b_for_y(self, y: float) -> float:
        if self._y0 <= y <= self._y0 + self._h:
            return (y - self._y0) / self._h * (self._bo - self._bu) + self._bu
        else:
            return self._bo

    def get_n_m_graph(self, e_top: float, e_bottom: float, h: float, type_of_diagram: int) -> tuple[int, int, list[
        Any]] | None:
        """the function returns normal force and moment relative of bottom of the section
                + list for graphic with yi, stress
                :returns normal force kN
                        moment  kNm"""
        dn = self._h / self._n
        normal_force = 0
        moment = 0
        list_for_graphic = []  # [[yi, si],..]
        for i in range(self._n):
            yi = (i + 0.5) * dn  # cm
            bi = (self._bo - self._bu) / self._h * yi + self._bu
            area_i = bi * dn * 100  # mm2
            yi += self._y0  # cm
            ec = get_ei_from_eo_eu_yi_h(eo=e_top, eu=e_bottom, h=h, yi=yi)
            sc = self._concrete.get_stress(ec=ec,
                                           typ_of_diagram=type_of_diagram)  # N/mm2
            if sc is None:
                return None
            normal_force += area_i * sc / 1000  # kN
            moment += area_i * sc * yi / 100000  # kNm
            list_for_graphic.append(ResultGraphConcrete(ec=ec, yi=yi, sc=sc))
        return normal_force, moment, list_for_graphic

    def get_copy_of_me(self):
        return AConcreteSection(bo=self._bo, bu=self._bu, y0=self._y0, h=self._h)


class ASteelLine(ElementOfSection):
    def __init__(self, d: float = 8, y: float = 5, n: float = 2, m: float = 1,
                 steel: str = InitiationValues.default_steel_class, s0: float = 0, typ_of_diagram: int = 0):
        self._f0_1k = 500 / 1.15
        self._fk = 525 / 1.15
        self._d = d
        self._y = y
        self._n = n
        self._m = m
        self._steel: DiagramSteel = self._get_diagram_for_the_steel(new_steel=steel)
        self._area = math.pi * (self._d * 0.5) ** 2 * self._m * self._n  # mm2
        self._s0 = s0
        self._e0 = self._steel.get_e_from_s(typ_of_diagram=typ_of_diagram, s=s0)
        self._color_rgba = get_random_color()
        self._color_str = get_str_from_color(color_rgba=self._color_rgba)
        self.e_init = 0

    @staticmethod
    def _get_diagram_for_the_steel(new_steel) -> None | DiagramSteel | DiagramCarbon:
        if new_steel in MaterialVariables.steel_for_concrete:
            return DiagramSteel(steel_type=new_steel)
        elif new_steel in MaterialVariables.carbon_class:
            return DiagramCarbon(carbon_class=new_steel)
        return None

    @property
    def important_coordinate(self, typ_of_diagram: int = 0) -> None | tuple[list[float | Any], list[float]] | tuple[
        list[float | Any], list[float | Any]]:
        return self._steel.important_coordinate(typ_of_diagram=typ_of_diagram)

    @property
    def color_str(self):
        return self._color_str

    @property
    def color_rgba(self) -> list:
        return self._color_rgba

    @property
    def color_QColor(self) -> QColor:
        return QColor(*self._color_rgba)

    def get_n_m_graph(self, e_top: float, e_bottom: float, h: float, type_of_diagram: int) -> tuple | None:
        """the function returns normal force and moment relative of bottom of the section
        + list for graphic with yi, stress
        :param h:
        :param e_bottom:
        :param e_top:
        :param type_of_diagram:
        returns normal force kN
                    moment  kNm"""
        es = get_ei_from_eo_eu_yi_h(eo=e_top, eu=e_bottom, yi=self._y, h=h) - self._e0  # e0 - prestress
        ss = self._steel.get_stress(ec=es, typ_of_diagram=type_of_diagram)
        if ss is None:
            print('steel stress is None', 'e_top = ', e_top, 'e_bottom = ', e_bottom)
            return None

        normal_force = self._area * (ss + self._s0) / 1000  # kN

        moment = normal_force * self._y / 100  # kNm
        #if normal_force < 0:
        #    moment = - moment
        graphic = ResultGraphSteel(yi=self._y, ss=ss, es=es, color=self.color_QColor)  # [[yi, si],..]
        return normal_force, moment, graphic

    def get_copy_of_me(self):
        return ASteelLine(d=self._d, y=self._y + 5, n=self._n, m=self._m,
                          steel=self._steel.name_of_class, s0=self._s0)

    def get_d_y_n_m_steel_s0(self) -> tuple:
        return self._d, self._y, self._n, self._m, self._steel, self._s0

    def new_d_y_n_m_steel_s0(self, d: float, y: float, n: int, m: int, steel, s0: float, type_of_diagram=0):
        self._d = d
        self._y = y
        self._n = n
        self._m = m
        self._steel = steel
        self._s0 = s0
        self._e0 = self._steel.get_e_from_s(typ_of_diagram=type_of_diagram, s=s0)
        self._area = math.pi * (self._d * 0.5) ** 2 * self._m * self._n  # mm2

    @property
    def steel(self):
        return self._steel

    @steel.setter
    def steel(self, new_steel: str):
        self._steel = self._get_diagram_for_the_steel(new_steel=new_steel)

    def get_prestressed_force(self) -> float:
        normal_force = self._area * self._s0 / 1000  # kN
        return - normal_force

    def update_s0(self, type_of_diagram: int):
        self._e0 = self._steel.get_e_from_s(typ_of_diagram=type_of_diagram, s=self._s0)

    def calculate_e_init(self, result__1: Result, result_1: Result, m_init: float, h: float):
        """
        :param h:
        :param m_init:
        :param result_1:    result i +1
        :param result__1:  result i -1
        """
        m__1 = result__1.moment
        m_1 = result_1.moment
        ec_1 = get_ei_from_eo_eu_z_h(eo=result_1.eo, eu=result_1.eu, h=h, z=self._z)
        ec__1 = get_ei_from_eo_eu_z_h(eo=result__1.eo, eu=result__1.eu, h=h, z=self._z)
        e_init = (ec_1 - ec__1) / (m_1 - m__1) * (m_init - m__1) + ec__1
        self.e_init = e_init


def get_random_color() -> list[int]:
    """rgb(255, 0, 0)"""
    min_v = 50
    max_v = 200
    rgba = [random.randint(min_v, max_v) for _ in range(3)]
    rgba.append(255)
    return rgba


def get_str_from_color(color_rgba: list[int]) -> str:
    return f"rgb({color_rgba[0]}, {color_rgba[1]}, {color_rgba[2]});"


def get_ei_from_eo_eu_yi_h(eo: float, eu: float, h: float, yi: float) -> float:
    return (eo - eu) * yi / h + eu
