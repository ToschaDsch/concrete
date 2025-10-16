import json

from PySide6.QtWidgets import QFileDialog

from moduls_to_calculate.classes_for_concrete_segment_and_steel import AConcreteSection, ASteelLine
from moduls_to_calculate.general_class_to_calculate import AllElementsOfTheSection

from variables.variables_the_program import Menus


def save_file_as(section: AllElementsOfTheSection, file=None):
    data: dict = data_to_dict(section=section)
    json_data = json.dumps(data)

    if file is None:
        self = Menus.general_window
        file = QFileDialog.getSaveFileName(self, 'save as', 'section',
                                           f"{Menus.file_name_extension} (*.{Menus.file_name_extension})")
        Menus.current_file = file
    try:
        fob = open(file[0], 'w')
        fob.write(json_data)
        fob.close()
        print('the file is saved')
    except (FileExistsError, Exception):
        print('file not found')
    Menus.save_file_name = file


def data_to_dict(section: AllElementsOfTheSection) -> dict:
    concrete = concrete_to_list(section=section)
    steel = steel_to_list(section=section)
    carbon = carbon_to_list(section=section)
    additional_plate = additional_plate_to_dict(section=section)
    other_variables = other_variables_to_dict(section=section)
    return {'concrete': concrete,
            'carbon': carbon,
            'steel': steel,
            'additional_plate': additional_plate,
            'other_variables': other_variables}


def concrete_to_list(section: AllElementsOfTheSection) -> list:
    list_of_all_sections = []
    for section_i in section.list_of_concrete_sections:
        list_of_all_sections.append(a_concrete_section_to_dict(section=section_i))

    return list_of_all_sections

def additional_plate_to_dict(section: AllElementsOfTheSection) -> dict:
    additional_section = section.addition_concrete
    additional_concrete ={"concrete_class":additional_section.concrete_class,
                          "b":additional_section.b,
                          "h":additional_section.h}
    additional_steel = {"steel_class":additional_section.steel_name,
                        "area":additional_section.steel.area,
                        "z":additional_section.steel.z,}
    return {"concrete":additional_concrete,
            "steel":additional_steel,
            "m_int":additional_section.m_int,
            "to_calculate":additional_section.calculate_with_top_plate}

def a_concrete_section_to_dict(section: AConcreteSection) -> dict:
    bo, bu, y0, h = section.get_bo_bu_y0_h()
    concrete_class = section.concrete.name_of_class
    dict_of_the_section = {'bo': bo,
                           'bu': bu,
                           'y0': y0,
                           'h': h,
                           'concrete_class': concrete_class}
    return dict_of_the_section


def steel_to_list(section: AllElementsOfTheSection) -> list:
    list_of_steel_lines = []
    type_of_diagram = section.type_of_diagram_steel
    for steel_line in section.list_of_steel:
        list_of_steel_lines.append(a_steel_line_to_dict(steel_line=steel_line, type_of_diagram=type_of_diagram))
    return list_of_steel_lines


def a_steel_line_to_dict(steel_line: ASteelLine, type_of_diagram: int) -> dict:
    d, y, n, m, steel, s0 = steel_line.get_d_y_n_m_steel_s0()
    steel_class = steel.name_of_class
    dict_of_the_steel_line = {'d': d,
                              'y': y,
                              'n': n,
                              'm': m,
                              'steel': steel_class,
                              's0': s0,
                              'diagram': type_of_diagram}
    return dict_of_the_steel_line


def carbon_to_list(section: AllElementsOfTheSection) -> dict:
    return {'m_int': section.carbon.m_int,
            'z': section.carbon.z,
            'area': section.carbon.area,
            'type': section.carbon.carbon_class,
            'calculate_with_carbon': section.carbon.calculate_with_carbon}


def other_variables_to_dict(section: AllElementsOfTheSection) -> dict:
    other_variables = {'diagram_concrete': section.type_of_diagram_concrete,
                       'diagram_steel': section.type_of_diagram_steel,
                       'n': section.n,
                       'normal_force': section.normal_force,
                       'dn': section.dn,
                       'n_de': section.n_de,
                       'eccentricity': section.eccentricity}
    return other_variables
