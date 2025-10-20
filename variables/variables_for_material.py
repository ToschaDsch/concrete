from dataclasses import dataclass
from ssl import DER_cert_to_PEM_cert

from PySide6.QtGui import QColor


@dataclass
class MaterialVariables:
    concrete = 'concrete'
    steel = 'steel'
    concrete_class = ('C12/15', 'C16/20', 'C20/25', 'C25/30', 'C30/37', 'C35/45', 'C40/50', 'C45/55', 'C50/60',
                      'C55/67', 'C60/75', 'C70/85', 'C80/95', 'C90/105')
    concrete_e_modul = {'C12/15': 27000, 'C16/20': 29000, 'C20/25': 30000, 'C25/30': 31000, 'C30/37': 33000,  # N/mm2
                        'C35/45': 34000, 'C40/50': 35000, 'C45/55': 36000, 'C50/60': 37000, 'C55/67': 38000,
                        'C60/75': 39000, 'C70/85': 41000, 'C80/95': 42000, 'C90/105': 44000}
    concrete_fck = {'C12/15': 12, 'C16/20': 16, 'C20/25': 20, 'C25/30': 25, 'C30/37': 30,  # N/mm2
                    'C35/45': 35, 'C40/50': 40, 'C45/55': 45, 'C50/60': 50, 'C55/67': 55,
                    'C60/75': 60, 'C70/85': 70, 'C80/95': 80, 'C90/105': 90}
    concrete_ec1 = {'C12/15': 1.8, 'C16/20': 1.9, 'C20/25': 2, 'C25/30': 2.1, 'C30/37': 2.2,  # %0
                    'C35/45': 2.25, 'C40/50': 2.3, 'C45/55': 2.4, 'C50/60': 2.45, 'C55/67': 2.5,
                    'C60/75': 2.6, 'C70/85': 2.7, 'C80/95': 2.8, 'C90/105': 2.8}
    concrete_ecu1 = {'C12/15': 3.5, 'C16/20': 3.5, 'C20/25': 3.5, 'C25/30': 3.5, 'C30/37': 3.5,  # %0
                     'C35/45': 3.5, 'C40/50': 3.5, 'C45/55': 3.5, 'C50/60': 3.5, 'C55/67': 3.2,
                     'C60/75': 3, 'C70/85': 2.8, 'C80/95': 2.8, 'C90/105': 2.8}
    concrete_ec2 = {'C12/15': 2, 'C16/20': 2, 'C20/25': 2, 'C25/30': 2, 'C30/37': 2,  # %0
                    'C35/45': 2, 'C40/50': 2, 'C45/55': 2, 'C50/60': 2, 'C55/67': 2.2,
                    'C60/75': 2.3, 'C70/85': 2.4, 'C80/95': 2.5, 'C90/105': 2.6}
    concrete_ecu2 = {'C12/15': 3.5, 'C16/20': 3.5, 'C20/25': 3.5, 'C25/30': 3.5, 'C30/37': 3.5,  # %0
                     'C35/45': 3.5, 'C40/50': 3.5, 'C45/55': 3.5, 'C50/60': 3.5, 'C55/67': 3.1,
                     'C60/75': 2.9, 'C70/85': 2.7, 'C80/95': 2.6, 'C90/105': 2.6}
    concrete_n = {'C12/15': 2, 'C16/20': 2, 'C20/25': 2, 'C25/30': 2, 'C30/37': 2,  # %0
                  'C35/45': 2, 'C40/50': 2, 'C45/55': 2, 'C50/60': 2, 'C55/67': 1.75,
                  'C60/75': 1.6, 'C70/85': 1.45, 'C80/95': 1.4, 'C90/105': 1.4}
    carbon_class = ('CARBOrefit_TYP1', 'CARBOrefit_TYP2', 'StoPox_SK_41', 'GRID Q95-95', 'Carbon4ReBAR',
                    'S&P_CFK_150/2000')
    carbon_ec2 = {'CARBOrefit_TYP1': 3.7, 'CARBOrefit_TYP2': 6.3, 'StoPox_SK_41': 10.49, 'GRID Q95-95': 6.7,
                  'Carbon4ReBAR': 8.4, 'S&P_CFK_150/2000': 10.5}  # %0
    carbon_fkf = {'CARBOrefit_TYP1': 768, 'CARBOrefit_TYP2': 1300, 'StoPox_SK_41': 1643, 'GRID Q95-95': 800,
                  'Carbon4ReBAR': 1270, 'S&P_CFK_150/2000': 1700}  # N/mm2
    steel_for_concrete = ('B500',
                          'St950/1050', 'St1375/1570', 'St1470/1670', 'St1570/1770', 'St1570/1770',
                          'St1660/1860')
    steel_for_concrete_fp01k = {'B500': 500,
                                'St950/1050': 950, 'St1375/1570': 1360, 'St1470/1670': 1420, 'St1570/1770': 1500,
                                'St1660/1860': 1600}
    steel_es = {'B500': 200000,
                'St950/1050': 205000, 'St1375/1570': 205000, 'St1470/1670': 205000, 'St1570/1770': 205000,
                'St1660/1860': 195000}
    steel_class = ('S235', 'S275', 'S355', 'S420', 'S460')
    steel_fyk = {'S235': 235, 'S275': 275, 'S355': 355, 'S420': 420, 'S460': 460}

    wood_class = ('C14', 'C16', 'C18', 'C20', 'C22', 'C24', 'C27', 'C30', 'C35', 'C40', 'C45', 'C50',
                  'D30', 'D35', 'D40', 'D50', 'D60', 'D70',
                  'GL24h', 'GL24c', 'GL28h', 'GL28c', 'GL30h', 'GL30c', 'GL32h', 'GL32c')
    wood_fmk = {'C14': 14, 'C16': 16, 'C18': 18, 'C20': 20, 'C22': 22, 'C24': 24, 'C27': 27, 'C30': 30, 'C35': 35,
                'C40': 40, 'C45': 45, 'C50': 50,
                'D30': 30, 'D35': 35, 'D40': 40, 'D50': 50, 'D60': 60, 'D70': 70,
                'GL24h': 24, 'GL24c': 24, 'GL28h': 28, 'GL28c': 28, 'GL30h': 30, 'GL30c': 30, 'GL32h': 32, 'GL32c': 32}
    wood_gm = 1.3  # gamma_M
    D = (6, 8, 10, 12, 14, 16, 20, 25, 28, 32, 40)


class ResultGraphConcrete:
    def __init__(self, ec: float, yi: float, sc: float):
        self.ec = ec
        self.yi = yi
        self.sc = sc


class ResultGraphSteel:
    def __init__(self, yi: float, ss: float, es: float, color: QColor):
        self.yi: float = yi
        self.ss: float = ss
        self.es: float = es
        self.color: QColor = color


class GeneralGraphicForResult:
    def __init__(self, graphic_for_concrete: list[list[ResultGraphConcrete]], graphic_for_steel: list[ResultGraphSteel],
                 graphic_for_carbon: ResultGraphSteel):
        self.graphic_for_concrete = graphic_for_concrete
        self.graphic_for_steel = graphic_for_steel
        self.graphic_for_carbon = graphic_for_carbon


class Result:
    def __init__(self, normal_force: float, moment: float, graph: GeneralGraphicForResult, e_top: float, e_bottom: float,
                 dn: float, sc: float, e_top_add_plate: float=0, w_bottom_add_plate: float=0):
        self.normal_force = normal_force  # normal force
        self.moment = moment  # moment
        self.graph: GeneralGraphicForResult = graph
        self.e_top = e_top  # relative deformation
        self.e_bottom = e_bottom
        self.dn = dn
        self.sc = sc
        self.e_top_add_plate = e_top_add_plate
        self.e_bottom_add_plate = w_bottom_add_plate

    def __str__(self):
        return f"m={self.moment}, n={self.normal_force}, eo={self.e_top}, eu={self.e_bottom}, dn = {self.dn}"
