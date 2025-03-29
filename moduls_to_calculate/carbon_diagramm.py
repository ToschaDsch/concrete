from moduls_to_calculate.diagram import Diagram
from variables.variables_for_material import MaterialVariables
from variables.variables_the_program import InitiationValues


class DiagramCarbon(Diagram):

    def __init__(self, carbon_class: str = InitiationValues.default_carbon_class):
        """carbon_class: S&P SFK 150/2000... """
        self._carbon_class = carbon_class
        self._fkf: float = MaterialVariables.carbon_fkf[carbon_class]
        self._ecu2: float = MaterialVariables.carbon_ec2[carbon_class] / 1000

    @property
    def name_of_class(self):
        return self._carbon_class

    def get_stress(self, ec: float, typ_of_diagram: int = 0) -> float | None:
        """typ_of_diagram: 0 - linear, 1 - nonlinear
        ec = ec*1000"""
        if ec == 0:
            return 0
        sign = ec / abs(ec)
        ec = abs(ec)
        if ec < self._ecu2:
            return ec / self._ecu2 * self._fkf * sign
        else:
            return None

    def get_max_x_y(self, typ_of_diagram: int = 0) -> tuple[float, float]:
        return self._ecu2, self._fkf

    def important_coordinate(self, typ_of_diagram: int = 0) -> ([float, float], [float, float]):
        return [self._ecu2, self._fkf], [self._ecu2, self._fkf]

    @property
    def es_max(self) -> float:
        return self._ecu2

    def get_e_from_s(self, s: float, typ_of_diagram: int = 0) -> float | None:
        """ the function calculates relative displacement of the steel from stress s0"""
        if s == 0:
            return 0
        sign = s / abs(s)
        s = abs(s)
        if s <= self._fkf:
            return s / self._fkf * self._ecu2 * sign
        else:
            return None
