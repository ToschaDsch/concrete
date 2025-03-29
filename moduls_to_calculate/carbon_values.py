from moduls_to_calculate.carbon_diagramm import DiagramCarbon
from moduls_to_calculate.classes_for_concrete_segment_and_steel import ElementOfSection
from variables.variables_for_material import ResultGraphSteel, Result
from variables.variables_the_program import InitiationValues, MyColors


class CarbonSegment(ElementOfSection):
    def __init__(self, a: float = 0, z: float = 1, m_int: int = 0,
                 carbon: str = InitiationValues.default_carbon_class):
        self._carbon_class = carbon
        self._area: float = a  # area, cm2)
        self._carbon_diagram: DiagramCarbon = DiagramCarbon(carbon_class=carbon)
        self._z: float = z  # distance form the bottom of the section to center of the carbon
        self.m_int: float = m_int  # initialisation moment for the carbon
        self.calculate_with_carbon: bool = False
        self.color_QColor = MyColors.carbon_stress
        self.m_1 = 0  # moment m_i-1
        self.e_top_1 = 0
        self.e_bottom_1 = 0
        self.e_init = 0

    @property
    def area(self) -> float:
        return self._area

    @area.setter
    def area(self, new_area: float):
        self._area = new_area

    @property
    def carbon_class(self):
        return self._carbon_class

    @carbon_class.setter
    def carbon_class(self, new_class: str):
        self._carbon_class = new_class
        self._carbon_diagram: DiagramCarbon = DiagramCarbon(carbon_class=new_class)

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, new_z: float):
        self._z = new_z

    @property
    def carbon_diagram(self):
        return self._carbon_diagram

    @carbon_diagram.setter
    def carbon_diagram(self, new_diagram: DiagramCarbon):
        self._carbon_diagram = new_diagram

    def get_n_m_graph(self, e_top: float, e_bottom: float, h: float, type_of_diagram: int) -> (float, float):
        """the function returns normal force and moment relative of bottom of the section
        + list for graphic with yi, stress
        :returns normal force kN
                    moment  kNm"""
        es = get_ei_from_eo_eu_z_h(eo=e_top, eu=e_bottom, z=self._z, h=h) - self.e_init

        ss = self._carbon_diagram.get_stress(ec=es)
        if ss is None:
            return None

        normal_force = self._area * ss / 10  # kN
        moment = - normal_force * self._z / 100  # kNm
        list_for_graphic = ResultGraphSteel(yi=self._z, ss=ss, es=es, color=self.color_QColor)  # [[yi, si],..]
        return normal_force, moment, list_for_graphic

    def get_null_graphic(self):
        return ResultGraphSteel(yi=self._z, ss=0, es=0, color=self.color_QColor)  # [[yi, si],..]

    def get_copy_of_me(self):
        pass

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
        print('e_init = ', e_init)


def get_ei_from_eo_eu_z_h(eo: float, eu: float, h: float, z: float) -> float:
    return (eu - eo) * (h + z) / h + eo
