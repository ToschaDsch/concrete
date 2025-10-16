import json

from PySide6.QtWidgets import QFileDialog

from moduls_to_calculate.classes_for_concrete_segment_and_steel import AConcreteSection, ASteelLine
from variables.variables_the_program import Menus


def open_file(self) -> dict | bool:
    data = open_file_menu(self)
    if data is False:
        return False
    json_data = json.loads(data)
    print(json_data)
    try:
        list_of_concrete_sections: list = transform_from_json_to_concrete(json_data['concrete'])
        list_of_steel: list = transform_from_json_to_steel(json_data['steel'])
        dict_of_other_variables: dict = json_data['other_variables']
        if 'carbon' in json_data:
            carbon: dict = json_data['carbon']
        else:
            carbon = {}
        if 'additional_plate' in json_data:
            additional_plate: dict = json_data['additional_plate']
        else:
            additional_plate = {}
    except TypeError:
        print('error by file opening')
        return False
    return {'list_of_concrete_sections': list_of_concrete_sections,
            'list_of_steel': list_of_steel,
            'carbon': carbon,
            "additional_plate": additional_plate,
            'other_variables': dict_of_other_variables,
            }


def transform_from_json_to_concrete(json_data) -> list[AConcreteSection]:
    new_list_of_concrete = []
    for data_i in json_data:
        bo = float(data_i['bo'])
        bu = float(data_i['bu'])
        y0 = float(data_i['y0'])
        h = float(data_i['h'])
        concrete_class = data_i['concrete_class']
        new_section = AConcreteSection(bo=bo, bu=bu, y0=y0, h=h, concrete_class=concrete_class)
        new_list_of_concrete.append(new_section)
    return new_list_of_concrete


def transform_from_json_to_steel(json_data) -> list[ASteelLine]:
    new_list_of_steel = []
    for data_i in json_data:
        d = float(data_i['d'])
        y = float(data_i['y'])
        n = float(data_i['n'])
        m = float(data_i['m'])
        steel = data_i['steel']
        s0 = data_i['s0']
        if 'diagram' in data_i:
            type_of_diagram = data_i['diagram']
        else:
            type_of_diagram = 0
        new_section = ASteelLine(d=d, y=y, n=n, m=m, steel=steel, s0=s0, typ_of_diagram=type_of_diagram)
        new_list_of_steel.append(new_section)
    return new_list_of_steel


def open_file_menu(self) -> bool | str:
    tf = QFileDialog.getOpenFileName(self, 'open', None,
                                     f"{Menus.file_name_extension} (*.{Menus.file_name_extension})")
    try:
        name = tf[0]
        Menus.save_file_name = tf
        Menus.current_file = tf
        tf = open(name)  # or tf = open(tf, 'r')
        data = tf.read()
        tf.close()
    except (FileExistsError, Exception):
        print('file not found')
        return False
    name = name.split(".")[0]
    name = name.split("/")[-1]
    name = f'{Menus.name_of_the_program} {name}'

    self.setWindowTitle(name)
    return data
