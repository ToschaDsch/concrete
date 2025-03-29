from abc import ABC, abstractmethod

from PySide6.QtGui import QColor

from variables.variables_for_material import MaterialVariables
from variables.variables_the_program import InitiationValues


class Diagram(ABC):
    @abstractmethod
    def get_stress(self, ec: float, typ_of_diagram: int = 0) -> float | None:
        pass

    @abstractmethod
    def name_of_class(self):
        pass

    @abstractmethod
    def get_max_x_y(self, typ_of_diagram: int = 0) -> tuple[float, float]:
        pass

    @abstractmethod
    def important_coordinate(self, typ_of_diagram: int = 0) -> ([float, float], [float, float]):
        pass


class DiagramConcrete(Diagram):

    def __init__(self, concrete_class: str = InitiationValues.default_concrete_class):
        """concrete_class: 'C25/30', """
        self._concrete_class = concrete_class
        self._fcd: float = MaterialVariables.concrete_fck[concrete_class] * 0.85 / 1.5
        self._ecu2: float = MaterialVariables.concrete_ecu2[concrete_class] / 1000
        self._ec2: float = MaterialVariables.concrete_ec2[concrete_class] / 1000
        self._ecm: float = MaterialVariables.concrete_e_modul[concrete_class]
        self._ecu1: float = MaterialVariables.concrete_ecu1[concrete_class] / 1000
        self._ec1: float = MaterialVariables.concrete_ec1[concrete_class] / 1000
        self._fcm: float = MaterialVariables.concrete_fck[concrete_class] + 8
        self._n: float = MaterialVariables.concrete_n[concrete_class]
        self._k: float = 1.05 * self._ec1 / self._fcm * self._ecm

    @property
    def name_of_class(self):
        return self._concrete_class

    def get_stress(self, ec: float, typ_of_diagram: int = 0) -> float | None:
        """typ_of_diagram: 0 - linear, 1 - nonlinear
        ec = ec*1000"""
        if ec <= 0:
            return 0
        match typ_of_diagram:
            case 0:
                if ec < self._ec2:
                    if self._concrete_class not in ('C55/67', 'C60/75', 'C70/85', 'C80/95', 'C90/105'):
                        return 1000 * (ec - 250 * ec ** 2) * self._fcd
                    else:
                        return (1 - (1 - ec / self._ec2) ** self._n) * self._fcd
                elif ec <= self._ecu2:
                    return self._fcd
                else:
                    return None
            case 1:  # nonlinear
                if ec < self._ecu1:
                    n = ec / self._ec1
                    return self._fcm * (self._k * n - n ** 2) / (1 + (self._k - 2) * n)
                else:
                    return None

    def get_max_x_y(self, typ_of_diagram: int = 0) -> tuple[float, float]:
        match typ_of_diagram:
            case 0:
                return self._ecu2, self._fcd
            case 1:
                return self._ecu1, self._fcm

    def important_coordinate(self, typ_of_diagram: int = 0) -> ([float, float], [float, float]):
        match typ_of_diagram:
            case 0:
                return [self._ec2, self._fcd], [self._ecu2, self._fcd]
            case 1:
                n = 1
                s_end = self._fcm * (self._k * n - n ** 2) / (1 + (self._k - 2) * n)
                return [self._ec1, self._fcm], [self._ecu1, s_end]


class DiagramSteel(Diagram):
    def __init__(self, steel_type: str = InitiationValues.default_steel_class):
        self._steel_type = steel_type
        self._fd = MaterialVariables.steel_for_concrete_fp01k[steel_type] / 1.15
        self._es = MaterialVariables.steel_es[steel_type]
        self._e0 = self._fd / self._es
        self._eud = 0.025
        if self._steel_type == MaterialVariables.steel_for_concrete[0]:
            self._fdk: float = 525 / 1.15
        else:
            self._fdk: float = int(self._steel_type[-4:]) / 1.15

    def get_stress(self, ec: float, typ_of_diagram: int = 0) -> float | None:
        """typ_of_diagram: 0 - constant, 1 - linear
        ec = ec *1000"""
        if ec == 0:
            return 0
        sign = ec / abs(ec)
        ec = abs(ec)
        if ec <= self._e0:  # elastic
            return ec / self._e0 * self._fd * sign
        elif ec <= self._eud:
            match typ_of_diagram:
                case 0:  # 0 - constant plastic
                    return self._fd * sign
                case 1:  # 1 linear plastic
                    return ((ec - self._e0) / (self._eud - self._e0) * (self._fdk - self._fd) + self._fd) * sign
        else:
            print('ec = ', ec, self._eud)
            return None

    def get_e_from_s(self, s: float, typ_of_diagram: int = 0) -> float | None:
        """ the function calculates relative displacement of the steel from stress s0"""
        if s == 0:
            return 0
        sign = s / abs(s)
        s = abs(s)
        if s <= self._fd:
            return s / self._fd * self._e0 * sign
        elif s <= self._fdk:
            match typ_of_diagram:
                case 0:  # 0 - constant plastic
                    return self._e0 * sign
                case 1:  # 1 linear plastic
                    return ((s - self._fd) / (self._fdk - self._fd) * (self._eud - self._e0) + self._e0) * sign
        else:
            return None

    @property
    def es_max(self) -> float:
        return self._eud

    @property
    def name_of_class(self):
        return self._steel_type

    def get_max_x_y(self, typ_of_diagram: int = 0) -> tuple[float, float]:
        match typ_of_diagram:
            case 0:
                return self._eud, self._fd
            case 1:
                return self._eud, self._fdk

    def important_coordinate(self, typ_of_diagram: int = 0) -> ([float, float], [float, float]):
        match typ_of_diagram:
            case 0:
                return [self._e0, self._fd], [self._eud, self._fd]
            case 1:
                return [self._e0, self._fd], [self._eud, self._fdk]


class DiagramToDraw:
    def __init__(self, coordinates: [], important_coordinate: [], color: QColor):
        self.coordinates: [] = coordinates
        self.important_coordinate = important_coordinate
        self.color = color
