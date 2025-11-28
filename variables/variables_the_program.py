from dataclasses import dataclass

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from variables.variables_for_material import MaterialVariables


@dataclass
class Menus:
    general_window = None
    save_file_name: str = 'default'
    current_file = None
    name_of_the_program = 'section'
    file_name_extension: str = 'sec'
    screen_width: int = 100
    screen_height: int = 100
    icon: str = './/icons//icon.png'

    font_height: int = 15

    table_insert: bool = False

    b_left_side: int = 400
    b_center: int = 400
    h_top: int = 400
    h_center: int = 150
    scale_canvas_section: float = 0.9
    scale_canvas_diagram: float = scale_canvas_section
    board_canvas_diagram: float = h_top * 0.05
    percent_board_left_canvas: float = 0.08
    b_right_side: int = 200

    max_steps_for_slider: int = 100
    sliders_width: int = b_center + b_left_side
    slider_label_height = 15

    max_recursion: int = 100
    radius_for_diagram_strain_circles: int = 5
    width_line_edit: int = 100
    normal_force_length = 100
    normal_force_height = 20


@dataclass
class InitiationValues:
    normal_force = 0
    eccentricity = 0  # for normal force
    n = 20
    d_e = 100
    d_n = 0.1
    default_concrete_class: str = MaterialVariables.concrete_class[3]
    default_steel_class: str = MaterialVariables.steel_for_concrete[0]
    default_carbon_class: str = MaterialVariables.carbon_class[0]
    # concrete
    b_concrete = 10
    h_concrete = 20
    # steel
    diameter_steel = 8
    m_steel = 1
    n_steel = 2
    y_steel = 5
    s0_steel = 0
    # carbon
    a_carbon = 5
    z_carbon = 2
    m_int_carbon = 2
    # addition concrete
    h_add = 20
    b_add = 20


@dataclass
class PenThicknessToDraw:
    boards = 2
    axis = 1
    steel_section = 1
    graph_diagram = 1
    addition_lines_for_diagram = 1
    stress_concrete = 1
    stress_steel = 5
    strains_section = 1


@dataclass
class MyColors:
    background = QtGui.QColor(230, 230, 230)
    carbon = QColor(0, 130, 130)
    carbon_stress = QColor(0, 180, 180)
    concrete = QColor(150, 150, 150)
    concrete_addition = QColor(180, 150, 150)
    concrete_diagram = QColor(150, 0, 0)
    concrete_diagram_polygon = QColor(150, 0, 0, 120)
    concrete_boards = QColor(100, 100, 100)
    concrete_addition_plate = QColor(150, 100, 100)
    normal_force = QColor(100, 200, 0)
    axis = QColor(100, 100, 100)
    addition_lines = QColor(100, 100, 100)
    strains_section = QColor(100, 100, 100)
    label_slider_lines = QColor(100, 250, 0)
    label_slider_background = Qt.GlobalColor.lightGray
    steel_additional_plate = QColor(250, 150, 150)


@dataclass
class TypeOfDiagram:
    concrete_linear = 'Beton linear'
    concrete_nonlinear = 'Beton nonlinear'
    steel_linear = 'Stahl linear'
    steel_nonlinear = 'Stahl nonlinear'


@dataclass
class MenuNames:
    concrete_diagram = 'Diagramm für Beton'
    steel_diagram = 'Diagramm für Stahl'
    label_n_top = 'das kleinste Teil des Betonsegments wird'
    label_n_for = 'auf'
    label_n_after = 'verteilt'
    recalculate = 'Berechnen'
    convergence = 'Konvergenz - '
    n_de_info = 'Diagramme werden auf'
    explanation_normal_force = 'Zug ist positiv'
    label_concrete = "Beton"
    label_steel = "Bewehrung"
    strengthening_concrete = "Verstärkung mit Beton oben"
    strengthening_carbon = "Verstärkung mit carbon unten"
    b_is = 'b = , cm'    # for addition plate
    h_is = 'h = , cm'    # for addition plate
    stress_concrete = '**************** Betonstress ****************'
    general_section = 'Hauptquerschnitt'
    addition_plate = 'Aufbeton'
    sigma_c = "σc = "

@dataclass
class Names:
    axes_concrete = ('εc', 'σc')
    axes_steel = ('εs', 'σs')
