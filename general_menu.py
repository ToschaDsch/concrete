from functools import partial

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QIcon, QPolygonF, QColor, QFont
from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QPushButton, QComboBox, QTableWidgetItem, QButtonGroup, QRadioButton, QLineEdit, QSlider, QCheckBox

from modul_to_draw.addition_functions_to_draw import make_intermediate_result_for_the_graphic, \
    get_scale_x_y_for_diagram, \
    make_polygon_to_draw_concrete, draw_a_graph_steel, draw_lines_above_concrete_diagram, get_y0
from moduls_to_calculate.general_class_to_calculate import AllElementsOfTheSection
from moduls_to_calculate.classes_for_concrete_segment_and_steel import AConcreteSection, ASteelLine

from moduls_to_calculate.diagram import DiagramToDraw
from save_open.open import open_file
from save_open.save import save_file_as
from variables import variables_the_program
from variables.variables_the_program import Menus, MyColors, PenThicknessToDraw, TypeOfDiagram, Names, MenuNames, \
    InitiationValues
from variables.variables_for_material import MaterialVariables, ResultGraphConcrete, ResultGraphSteel, \
    GeneralGraphicForResult, Result


class GeneralWindow(QMainWindow):
    def __init__(self, *args):
        super(GeneralWindow, self).__init__()

        self.setWindowTitle(Menus.name_of_the_program)

        general_layout = QVBoxLayout()


        # variables to calculate
        self._section = AllElementsOfTheSection(concrete_class=MaterialVariables.concrete_class[3])
        self._m_max = 0  # max moment after the calculation
        self._mi = 0  # current moment to draw
        self._ni = 0  # current normal force to draw

        # menu up
        self.make_toolbar_with_buttons()

        # variables menu
        self.label_section_canvas = QLabel()
        self.label_diagram_canvas = QLabel()
        b = variables_the_program.Menus.b_left_side
        h = variables_the_program.Menus.h_top

        # canvas section
        self.canvas_section = QtGui.QPixmap(b, h)
        self.label_section_canvas.setPixmap(self.canvas_section)
        self.painter_section = QtGui.QPainter(self.canvas_section)
        font = QFont('Century Gothic', Menus.font_height)
        self.painter_section.setFont(font)

        # canvas diagram
        b = variables_the_program.Menus.b_center
        self.canvas_diagram = QtGui.QPixmap(b, h)
        self.label_diagram_canvas.setPixmap(self.canvas_diagram)
        self.painter_diagram = QtGui.QPainter(self.canvas_diagram)
        self.painter_diagram.setFont(font)

        # top layouts
        top_layout = QHBoxLayout()
        section_layout = QVBoxLayout()
        diagram_layout = QVBoxLayout()
        self.load_layout_draw_section_diagram(section_layout=section_layout,
                                              diagram_layout=diagram_layout)

        self.linear_concrete = QRadioButton(TypeOfDiagram.concrete_linear)
        self.nonlinear_concrete = QRadioButton(TypeOfDiagram.concrete_nonlinear)
        self.group_concrete = QButtonGroup()
        self.linear_steel = QRadioButton(TypeOfDiagram.steel_linear)
        self.nonlinear_steel = QRadioButton(TypeOfDiagram.steel_nonlinear)
        self.group_steel = QButtonGroup()
        right_top_layout = QVBoxLayout()
        self.line_edit_n = QLineEdit(str(InitiationValues.n))
        self.line_edit_dn = QLineEdit(str(InitiationValues.d_n))
        self.line_edit_n_de = QLineEdit(str(InitiationValues.d_e))
        self.line_edit_normal_force = QLineEdit(str(InitiationValues.normal_force))
        self.line_edit_eccentricity = QLineEdit(str(InitiationValues.eccentricity))
        self.label_m_lim = QLabel('0')  # max normal force
        self.load_right_top_layout(layout=right_top_layout)

        top_layout.addLayout(section_layout)  # right layout
        top_layout.addLayout(diagram_layout)  # middle layout
        top_layout.addLayout(right_top_layout)  # left layout
        general_layout.addLayout(top_layout)

        # central horizontal layout
        self.label_current_moment_m_i = QLabel('0')  # current moment
        self.label_current_normal_force_n_i = QLabel('0')  # current normal force
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedWidth(Menus.sliders_width)
        self.label_for_slider = QLabel()
        b = Menus.sliders_width
        h = Menus.slider_label_height
        self.canvas_slider = QtGui.QPixmap(b, h)
        self.canvas_slider.fill(MyColors.label_slider_background)
        self.label_for_slider.setPixmap(self.canvas_slider)
        self.painter_slider = QtGui.QPainter(self.canvas_slider)
        self.painter_slider.setFont(font)
        self.load_layout_center_horizontal(layout=general_layout)

        # bottom layouts
        # left part concrete
        bottom_layout = QHBoxLayout()
        concrete_layout = QVBoxLayout()
        self.combobox_objects_concrete_general = QComboBox()
        self.button_plus_concrete = QPushButton("+")
        self.button_minus_concrete = QPushButton("-")
        self.table_concrete = QTableWidget()
        self.option_plate_top_bottom = QVBoxLayout()
        bottom_layout.addLayout(concrete_layout)
        self.load_layout_concrete(concrete_layout)

        # central part steel
        steel_layout = QVBoxLayout()
        self.button_plus_steel = QPushButton("+")
        self.button_minus_steel = QPushButton("-")
        self.table_steel = QTableWidget()
        self.steel_layout = QVBoxLayout()
        self.list_of_combobox_steel = []
        bottom_layout.addLayout(steel_layout)
        self.load_layout_steel(steel_layout)
        general_layout.addLayout(bottom_layout)

        # addition layouts at the bottom
        extra_bottom_layout = QHBoxLayout()
        general_layout.addLayout(extra_bottom_layout)
        self.combobox_addition_concrete = QComboBox()
        self.table_additional_concrete = QTableWidget()
        self.line_edit_b = QLineEdit('')
        self.line_edit_h = QLineEdit('')
        self.checkbox_addition_top_plate = QCheckBox(MenuNames.strengthening_concrete)
        self.checkbox_carbon = QCheckBox(MenuNames.strengthening_carbon)
        self.table_carbon = QTableWidget()
        self.load_layout_extra_layout(extra_layout=extra_bottom_layout)

        widget = QWidget()
        widget.setLayout(general_layout)
        self.setCentralWidget(widget)

    def load_layout_extra_layout(self, extra_layout: QHBoxLayout):
        self.load_concrete_strengthening(extra_layout=extra_layout)
        self.load_carbon_strengthening(extra_layout=extra_layout)

    def load_concrete_strengthening(self, extra_layout: QHBoxLayout):
        layout_concrete_strengthening = QVBoxLayout()
        extra_layout.addLayout(layout_concrete_strengthening)
        self.checkbox_addition_top_plate.stateChanged.connect(self.calculate_with_top_plate)
        layout_concrete_strengthening.addWidget(self.checkbox_addition_top_plate)
        self.load_concrete_strengthening_plate(layout=layout_concrete_strengthening)

    def load_concrete_strengthening_plate(self, layout: QVBoxLayout):
        layout_concrete = QHBoxLayout()
        label = QLabel(MenuNames.label_concrete)
        layout_concrete.addWidget(label)

        # combobox addition concrete
        objects = MaterialVariables.concrete_class
        for name_i in objects:
            self.combobox_addition_concrete.addItem(name_i)
        self.combobox_addition_concrete.setEnabled(False)
        self.combobox_addition_concrete.setCurrentIndex(3)
        self.combobox_addition_concrete.currentIndexChanged.connect(
            self.change_index_of_combobox_addition_concrete)
        layout_concrete.addWidget(self.combobox_addition_concrete)

        # b =
        label_b = QLabel(MenuNames.b_is)
        layout_concrete.addWidget(label_b)
        self.line_edit_b.setText(str(InitiationValues.b_add))
        self.line_edit_b.setEnabled(False)
        self.line_edit_b.textChanged.connect(self.text_changed_b_addition_plate)
        layout_concrete.addWidget(self.line_edit_b)

        # h =
        label_h = QLabel(MenuNames.h_is)
        layout_concrete.addWidget(label_h)
        self.line_edit_h.setText(str(InitiationValues.h_add))
        self.line_edit_h.setEnabled(False)
        self.line_edit_h.textChanged.connect(self.text_changed_h_addition_plate)
        layout_concrete.addWidget(self.line_edit_h)

        layout.addLayout(layout_concrete)
        layout_steel = QHBoxLayout()
        layout.addLayout(layout_steel)
        header = ('A, cm2', 'Typ', 'z, cm', 'M_int, kNm')
        b = int((variables_the_program.Menus.b_center + variables_the_program.Menus.b_right_side +
                 variables_the_program.Menus.b_left_side) / 2)
        self.table_additional_concrete.setFixedWidth(b)
        self.table_additional_concrete.setColumnCount(len(header))
        self.table_additional_concrete.setHorizontalHeaderLabels(header)
        bi = b / len(header) * 0.95
        for i in range(len(header)):
            self.table_additional_concrete.setColumnWidth(i, int(bi))
        self.table_additional_concrete.itemChanged.connect(self.addition_steel_table_changed_item)
        self.table_additional_concrete.itemSelectionChanged.connect(self.selection_changed_carbon)
        self.table_additional_concrete.setEnabled(False)

        layout_steel.addWidget(self.table_additional_concrete)
        Menus.table_insert = True
        steel = self._section.addition_concrete.steel
        self.table_additional_concrete.insertRow(0)
        # A, cm2
        self.table_additional_concrete.setItem(0, 0, QTableWidgetItem(str(steel.area)))
        # typ, cm2
        combobox_steel = QComboBox()
        steel_name = self._section.addition_concrete.steel.steel_name
        for steel_name_i in MaterialVariables.steel_for_concrete:
            combobox_steel.addItem(steel_name_i)
        index = MaterialVariables.steel_for_concrete.index(steel_name)
        combobox_steel.setCurrentIndex(index)
        row_number_in_list = 0
        combobox_steel.currentIndexChanged.connect(self.change_index_of_combobox_addition_steel)
        self.table_additional_concrete.setCellWidget(0, 1, combobox_steel)
        # z, cm
        self.table_additional_concrete.setItem(0, 2, QTableWidgetItem(str(steel.z)))
        # m_int, kNm
        self.table_additional_concrete.setItem(0, 3, QTableWidgetItem(str(self._section.addition_concrete.m_int)))
        Menus.table_insert = False

    def addition_steel_table_changed_item(self, item):
        """change the addition steel"""
        if Menus.table_insert:
            return None
        text = item.text()
        if text == '' or text == '.' or text == '-.':
            return False
        j = item.column()
        t = float(text)
        try:
            match j:
                case 0: # area
                    self._section.addition_concrete.steel.area = float(t)
                case 2: #z
                    self._section.addition_concrete.steel.z = float(t)
                case 3:
                    self._section.addition_concrete.m_int = float(t)
        except Exception as inst:
            print(type(inst))
            return None
        self.draw_date_and_results()
        return None

    def change_index_of_combobox_addition_steel(self, new_index):
        new_steel_name = MaterialVariables.steel_for_concrete[new_index]
        self._section.addition_concrete.steel_name = new_steel_name
        self._section.is_calculated = False
        self.draw_date_and_results()

    def text_changed_b_addition_plate(self, new_text: str):
        try:
            b = float(new_text)
            self._section.addition_concrete.b = b
            print(b)
            self.draw_all()
        except Exception as inst:
            print(type(inst), new_text)
            return None

    def text_changed_h_addition_plate(self, new_text: str):
        try:
            h = float(new_text)
            self._section.addition_concrete.h = h
            print(h)
            self.draw_all()
        except Exception as inst:
            print(type(inst), new_text)
            return None

    def load_carbon_strengthening(self, extra_layout: QHBoxLayout):
        layout_carbon_strengthening = QVBoxLayout()
        extra_layout.addLayout(layout_carbon_strengthening)
        self.checkbox_carbon.stateChanged.connect(self.calculate_with_carbon)
        layout_carbon_strengthening.addWidget(self.checkbox_carbon)

        header = ('A, cm2', 'Typ', 'z, cm', 'M_int, kNm')
        b = int((variables_the_program.Menus.b_center + variables_the_program.Menus.b_right_side +
                 variables_the_program.Menus.b_left_side) / 2)
        self.table_carbon.setFixedWidth(b)
        self.table_carbon.setColumnCount(len(header))
        self.table_carbon.setHorizontalHeaderLabels(header)
        bi = b / len(header) * 0.95
        for i in range(len(header)):
            self.table_carbon.setColumnWidth(i, int(bi))
        self.table_carbon.itemChanged.connect(self.carbon_table_changed_item)
        self.table_carbon.itemSelectionChanged.connect(self.selection_changed_carbon)
        self.table_carbon.setEnabled(False)

        layout_carbon_strengthening.addWidget(self.table_carbon)
        Menus.table_insert = True
        self.table_carbon.insertRow(0)
        # A, cm2
        self.table_carbon.setItem(0, 0, QTableWidgetItem('0'))
        # typ, cm2
        combobox_carbon = QComboBox()
        carbon_name = self._section.carbon.carbon_class
        for carbon_name_i in MaterialVariables.carbon_class:
            combobox_carbon.addItem(carbon_name_i)
        index = MaterialVariables.carbon_class.index(carbon_name)
        combobox_carbon.setCurrentIndex(index)
        row_number_in_list = 0
        combobox_carbon.currentIndexChanged.connect(self.change_index_of_combobox_carbon)
        self.table_carbon.setCellWidget(0, 1, combobox_carbon)
        # z, cm
        self.table_carbon.setItem(0, 2, QTableWidgetItem('0'))
        # m_int, kNm
        self.table_carbon.setItem(0, 3, QTableWidgetItem('0'))
        Menus.table_insert = False

    def change_index_of_combobox_carbon(self, new_index):
        new_carbon_name = MaterialVariables.carbon_class[new_index]
        self._section.carbon.carbon_class = new_carbon_name
        self._section.is_calculated = False
        self.draw_date_and_results()

    def calculate_with_carbon(self, check: bool):
        check = bool(check)
        self._section.carbon.calculate_with_carbon = bool(check)
        self.table_carbon.setEnabled(check)
        self.draw_all()
        self.checkbox_addition_top_plate.setChecked(False)

    def calculate_with_top_plate(self, check: bool):
        self._section.addition_concrete.calculate_with_top_plate = bool(check)

        self.table_additional_concrete.setEnabled(check)
        self.combobox_addition_concrete.setEnabled(check)
        self.line_edit_b.setEnabled(check)
        self.line_edit_h.setEnabled(check)
        self.checkbox_carbon.setChecked(False)
        b, h = self._section.get_b_h_max()
        self._section.addition_concrete.section.y0 = h
        self.draw_all()


    def selection_changed_carbon(self):
        pass

    def carbon_table_changed_item(self, item):
        """change a carbon segment"""
        if Menus.table_insert:
            return None
        text = item.text()
        if text == '' or text == '.' or text == '-.':
            return False
        j = item.column()
        t = float(text)
        try:
            match j:
                case 0:
                    self._section.carbon.area = float(t)
                case 2:
                    self._section.carbon.z = float(t)
                case 3:
                    self._section.carbon.m_int = float(t)
        except Exception as inst:
            print(type(inst))
            return None
        self.draw_date_and_results()
        return None

    def load_layout_center_horizontal(self, layout: QVBoxLayout):
        self.slider.setEnabled(False)
        self.slider.setFixedWidth(Menus.sliders_width)
        layout_center_horizontal = QHBoxLayout()

        layout.addLayout(layout_center_horizontal)
        layout_current_m_n = QHBoxLayout()
        label_m_i = QLabel('M_i, kNm = ')
        layout_current_m_n.addWidget(label_m_i)
        layout_current_m_n.addWidget(self.label_current_moment_m_i)

        label_n_i = QLabel('N_i, kN = ')
        layout_current_m_n.addWidget(label_n_i)
        layout_current_m_n.addWidget(self.label_current_normal_force_n_i)
        layout_center_horizontal.addLayout(layout_current_m_n)

        layout_slider = QVBoxLayout()
        self.slider.setMinimum(0)
        self.slider.setMaximum(Menus.max_steps_for_slider)
        self.slider.valueChanged.connect(self.value_changed)

        layout_slider.addWidget(self.label_for_slider)
        layout_slider.addWidget(self.slider)
        pen = QtGui.QPen(MyColors.label_slider_lines, PenThicknessToDraw.axis)
        self.painter_slider.setPen(pen)

        layout_center_horizontal.addLayout(layout_slider)
        layout.addLayout(layout_center_horizontal)

    def value_changed(self, i):
        self._mi = self._m_max * i / Menus.max_steps_for_slider
        self.label_current_moment_m_i.setText(str(round(self._mi, 2)))
        self.draw_all()

    def make_toolbar_with_buttons(self):
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_open = QAction(QIcon("icons//open.png"), 'open', self)
        button_open.setStatusTip('open')
        button_open.triggered.connect(self.open_file)
        toolbar.addAction(button_open)

        button_save = QAction(QIcon("icons//save.png"), 'save', self)
        button_save.setStatusTip('save')
        button_save.triggered.connect(self.save_file)
        toolbar.addAction(button_save)

    def open_file(self):
        new_date = open_file(self=self)
        if new_date is False:
            return None
        list_of_concrete_sections = new_date['list_of_concrete_sections']
        self.update_the_concrete_table(new_list_of_concrete_sections=list_of_concrete_sections)
        list_of_steel = new_date['list_of_steel']
        self.update_the_steel_table(new_list_of_steel=list_of_steel)
        self.send_other_variables_by_file_open(other_variables=new_date['other_variables'])
        if new_date['carbon']:
            self.update_carbon(new_date['carbon'])
        if 'additional_plate' in new_date:
            self.update_additional_plate(new_date['additional_plate'])
        return None

    def send_other_variables_by_file_open(self, other_variables: dict):
        # sent diagram
        diagram_concrete = int(other_variables['diagram_concrete'])
        match diagram_concrete:
            case 0:  # linear concrete
                self.linear_concrete.setChecked(True)
            case 1:  # nonlinear
                self.nonlinear_concrete.setChecked(True)
        diagram_steel = int(other_variables['diagram_steel'])
        match diagram_steel:
            case 0:  # linear concrete
                self.linear_steel.setChecked(True)
            case 1:  # nonlinear
                self.nonlinear_steel.setChecked(True)
        # sent variables
        n = int(other_variables['n'])
        self.line_edit_n.setText(str(n))
        normal_force = float(other_variables['normal_force'])
        self.line_edit_normal_force.setText(str(normal_force))
        eccentricity = float(other_variables['eccentricity'])
        self.line_edit_eccentricity.setText(str(eccentricity))
        dn = float(other_variables['dn'])
        self.line_edit_dn.setText(str(dn))
        n_de = int(other_variables['n_de'])
        self.line_edit_n_de.setText(str(n_de))

    def save_file(self):
        file = Menus.current_file
        save_file_as(section=self._section, file=file)

    def load_layout_diagram(self, layout: QVBoxLayout):
        layout.addWidget(self.label_diagram_canvas)

    def load_right_top_layout(self, layout: QVBoxLayout):
        """load all elements for the layout"""
        self.radiobutton_concrete(layout=layout)
        self.radiobutton_steel(layout=layout)
        self.layout_edit_n(layout=layout)
        self.layout_normal_force_and_eccentricity(layout=layout)
        self.layout_dn(layout=layout)
        self.layout_n_de(layout=layout)
        button_recalculate = QPushButton(MenuNames.recalculate)
        button_recalculate.clicked.connect(self.recalculate_it)
        layout.addWidget(button_recalculate)

        layout_m_lim = QHBoxLayout()
        label_m_lim = QLabel('M_lim, kNm = ')
        layout_m_lim.addWidget(label_m_lim)
        layout_m_lim.addWidget(self.label_m_lim)
        layout.addLayout(layout_m_lim)

    def layout_n_de(self, layout: QVBoxLayout):
        layout_n_de = QVBoxLayout()
        label_n_de_info = QLabel(MenuNames.n_de_info)
        layout_n_de_line = QHBoxLayout()
        label_n_de = QLabel('n_de = ')
        layout_n_de_line.addWidget(label_n_de)
        self.line_edit_n_de = QLineEdit(str(InitiationValues.d_e))
        self.line_edit_n_de.editingFinished.connect(self.change_n_de)
        self.line_edit_n_de.setFixedWidth(Menus.width_line_edit)
        layout_n_de_line.addWidget(self.line_edit_n_de)
        layout_n_de_line.addWidget(QLabel(MenuNames.label_n_after))
        layout_n_de.addWidget(label_n_de_info)
        layout_n_de.addLayout(layout_n_de_line)
        layout.addLayout(layout_n_de)

    def recalculate_it(self):
        self._section.is_calculated = self._section.recalculate()
        self.slider.setValue(0)
        self.draw_date_and_results()

    def layout_normal_force_and_eccentricity(self, layout: QVBoxLayout):
        layout_norm_force = QHBoxLayout()
        label_n = QLabel('N, kN =')
        self.line_edit_normal_force.editingFinished.connect(self.change_normal_force)
        self.line_edit_normal_force.setFixedWidth(Menus.width_line_edit)
        layout_norm_force.addWidget(label_n)
        layout_norm_force.addWidget(self.line_edit_normal_force)
        label_explanation = QLabel(MenuNames.explanation_normal_force)
        layout_norm_force.addWidget(label_explanation)
        layout.addLayout(layout_norm_force)
        layout_eccentricity = QHBoxLayout()
        layout_e0 = QLabel('e0, m = ')
        layout_eccentricity.addWidget(layout_e0)
        self.line_edit_eccentricity.editingFinished.connect(self.change_eccentricity)
        self.line_edit_eccentricity.setFixedWidth(Menus.width_line_edit)
        layout_eccentricity.addWidget(self.line_edit_eccentricity)
        layout.addLayout(layout_eccentricity)

    def layout_dn(self, layout: QVBoxLayout):
        layout_dn = QHBoxLayout()
        label_convergence = QLabel(MenuNames.convergence)
        label_dn = QLabel('dNmax, kN =')
        self.line_edit_dn.editingFinished.connect(self.change_dn)
        self.line_edit_dn.setFixedWidth(Menus.width_line_edit)
        layout.addWidget(label_convergence)
        layout_dn.addWidget(label_dn)
        layout_dn.addWidget(self.line_edit_dn)
        layout.addLayout(layout_dn)

    def change_dn(self):
        text = self.line_edit_dn.text()
        if text == '' or text == '.' or text == '-.' or text == '0':
            return False
        dn = abs(float(text))
        self._section.dn = dn
        self._section.is_calculated = False
        self.draw_date_and_results()

    def change_n_de(self):
        text = self.line_edit_n_de.text()
        if text == '' or text == '.' or text == '-.' or text == '0':
            return False
        n_de = abs(float(text))
        self._section.n_de = n_de
        self._section.is_calculated = False
        self.draw_date_and_results()

    def change_normal_force(self):
        text = self.line_edit_normal_force.text()
        text = text.replace(',', '.')
        if text == '' or text == '.' or text == '-.':
            return False
        normal_force = float(text)
        self._section.normal_force = normal_force
        self.draw_date_and_results()

    def change_eccentricity(self):
        text = self.line_edit_eccentricity.text()
        text = text.replace(',', '.')
        if text == '' or text == '.' or text == '-.':
            return False
        eccentricity = float(text)
        self._section.eccentricity = eccentricity
        self.draw_date_and_results()

    def layout_edit_n(self, layout: QVBoxLayout):
        layout_edit_top = QHBoxLayout()
        layout_edit_n = QHBoxLayout()
        label_for = QLabel(MenuNames.label_n_for)
        self.line_edit_n.editingFinished.connect(self.change_n)
        self.line_edit_n.setFixedWidth(Menus.width_line_edit)
        label_top = QLabel(MenuNames.label_n_top)
        layout_edit_top.addWidget(label_top)
        label_after = QLabel(MenuNames.label_n_after)
        layout_edit_n.addWidget(label_for)
        layout_edit_n.addWidget(self.line_edit_n)
        layout_edit_n.addWidget(label_after)
        layout.addLayout(layout_edit_top)
        layout.addLayout(layout_edit_n)
        self.draw_all()

    def change_n(self):
        """parts of segments in the concrete section"""
        text = self.line_edit_n.text()
        if text == '' or text == '.' or text == '-.':
            return False
        n = abs(int(text))
        self._section.n = n
        self.draw_date_and_results()

    def radiobutton_concrete(self, layout: QVBoxLayout):
        label_concrete = QLabel(MenuNames.concrete_diagram)
        layout.addWidget(label_concrete)
        self.linear_concrete.setChecked(True)
        self.linear_concrete.toggled.connect(partial(self.change_a_diagram, self.linear_concrete))
        self.group_concrete.addButton(self.linear_concrete)
        layout.addWidget(self.linear_concrete)
        self.nonlinear_concrete.toggled.connect(partial(self.change_a_diagram, self.nonlinear_concrete))
        self.group_concrete.addButton(self.nonlinear_concrete)
        layout.addWidget(self.nonlinear_concrete)

    def radiobutton_steel(self, layout: QVBoxLayout):
        label_steel = QLabel(MenuNames.steel_diagram)
        layout.addWidget(label_steel)
        self.linear_steel.setChecked(True)
        self.linear_steel.toggled.connect(partial(self.change_a_diagram, self.linear_steel))
        self.group_steel.addButton(self.linear_steel)
        layout.addWidget(self.linear_steel)
        self.nonlinear_steel.toggled.connect(partial(self.change_a_diagram, self.nonlinear_steel))
        self.group_steel.addButton(self.nonlinear_steel)
        layout.addWidget(self.nonlinear_steel)

    def change_a_diagram(self, button: QRadioButton, _: bool):
        if not button.isChecked():
            return None
        match button.text():
            case TypeOfDiagram.concrete_linear:
                self._section.type_of_diagram_concrete = 0
            case TypeOfDiagram.concrete_nonlinear:
                self._section.type_of_diagram_concrete = 1
            case TypeOfDiagram.steel_linear:
                self._section.type_of_diagram_steel = 0
            case TypeOfDiagram.steel_nonlinear:
                self._section.type_of_diagram_steel = 1
        self.draw_date_and_results()
        return None

    def load_layout_concrete(self, layout: QVBoxLayout):
        header = ('bu, cm.', 'bo, cm.', 't, cm')
        b = variables_the_program.Menus.b_left_side

        concrete_layout = QtWidgets.QHBoxLayout()
        self.load_layout_concrete_buttons_and_combobox(layout=layout)
        self.table_concrete.setFixedWidth(b)
        self.table_concrete.setFixedHeight(Menus.h_center)
        self.table_concrete.setColumnCount(len(header))
        self.table_concrete.setHorizontalHeaderLabels(header)
        bi = b / len(header) * 0.95
        for i in range(len(header)):
            self.table_concrete.setColumnWidth(i, int(bi))
        self.table_concrete.itemChanged.connect(self.concrete_table_changed_item)
        self.table_concrete.itemSelectionChanged.connect(self.selection_changed_concrete)
        concrete_layout.addWidget(self.table_concrete)

        default_element = self._section.list_of_concrete_sections[0]
        self.add_an_element_in_the_concrete_table(row_number=0, new_element=default_element)
        layout.addLayout(concrete_layout)

    def load_layout_concrete_buttons_and_combobox(self, layout: QVBoxLayout):
        layout_buttons = QHBoxLayout()
        layout.addLayout(layout_buttons)
        layout_buttons.addWidget(QLabel(MenuNames.label_concrete))
        layout_buttons.addWidget(self.button_plus_concrete)
        self.button_plus_concrete.clicked.connect(self.plus_an_element_of_concrete)
        layout_buttons.addWidget(self.button_minus_concrete)
        self.button_minus_concrete.clicked.connect(self.minus_an_element_of_concrete)
        self.button_minus_concrete.setEnabled(False)

        # combobox concrete
        objects = MaterialVariables.concrete_class
        for name_i in objects:
            self.combobox_objects_concrete_general.addItem(name_i)
        self.combobox_objects_concrete_general.setCurrentIndex(3)
        self.combobox_objects_concrete_general.currentIndexChanged.connect(
            self.change_index_of_combobox_object_concrete_general)
        layout_buttons.addWidget(self.combobox_objects_concrete_general)

    def change_index_of_combobox_object_concrete_general(self, index):
        """new concrete class"""
        self._section.concrete_class = MaterialVariables.concrete_class[index]
        self.draw_date_and_results()

    def change_index_of_combobox_addition_concrete(self, index):
        """new concrete class"""
        self._section.addition_concrete.concrete_class = MaterialVariables.concrete_class[index]
        self.draw_date_and_results()

    def concrete_table_changed_item(self, item) -> None | bool:
        """change a concrete section"""
        if Menus.table_insert:
            return None
        text = item.text()
        if text == '' or text == '.' or text == '-.' or text == '0':
            return False
        row = item.row()
        i = len(self._section.list_of_concrete_sections) - 1 - row
        j = item.column()
        t = float(text)
        section = self._section.list_of_concrete_sections[i]
        bo, bu, y0, h = section.get_bo_bu_y0_h()
        match j:
            case 0:
                bu = t
            case 1:
                bo = t
            case 2:
                h = t
        self._section.list_of_concrete_sections[i].new_bo_bu_y0_h(bo=bo, bu=bu, y0=y0, h=h)
        self._section.correct_new_concrete_section()
        b, h = self._section.get_b_h_max()
        self._section.addition_concrete.section.y0 = h
        self.draw_date_and_results()
        return None

    def steel_table_changed_item(self, item) -> None | bool:
        """change a concrete section"""
        if Menus.table_insert:
            return None
        text = item.text()
        if text == '' or text == '.' or text == '-.':
            return False
        i = item.row()
        j = item.column()
        text = text.replace(',', '.')
        t = float(text) if j != 5 else text
        n_section = len(self._section.list_of_steel) - 1 - i
        steel_line = self._section.list_of_steel[n_section]
        d, y, n, m, steel, s0 = steel_line.get_d_y_n_m_steel_s0()
        match j:
            case 0:
                return None
            case 1:
                d = t
            case 2:
                m = t
            case 3:
                n = t
            case 4:
                y = t
            case 6:
                s0 = t

        steel_line.new_d_y_n_m_steel_s0(d=d, y=y, n=n, m=m, steel=steel, s0=s0,
                                        type_of_diagram=self._section.type_of_diagram_steel)
        self.draw_date_and_results()

    def selection_changed_concrete(self):
        list_of_selected_items = self.table_concrete.selectedIndexes()
        rows = [x.row() for x in list_of_selected_items]
        """TODO draw it"""

    def selection_changed_steel(self):
        list_of_selected_items = self.table_steel.selectedIndexes()
        rows = [x.row() for x in list_of_selected_items]
        """TODO draw it"""

    def load_layout_steel(self, layout: QVBoxLayout):
        self.table_steel.verticalHeader().hide()
        header = ('Nr.', '⌀, mm.', 'm', 'n', 'y, cm', 'Type', 'σ0, N/mm2')
        b = variables_the_program.Menus.b_center + variables_the_program.Menus.b_right_side

        steel_layout = QtWidgets.QHBoxLayout()
        self.load_layout_steel_buttons(layout=layout)
        self.table_steel.setFixedWidth(b)
        self.table_steel.setColumnCount(len(header))
        self.table_steel.setHorizontalHeaderLabels(header)
        bi = b / len(header)
        for i in range(len(header)):
            self.table_steel.setColumnWidth(i, int(bi))
        self.table_steel.itemChanged.connect(self.steel_table_changed_item)
        self.table_steel.itemSelectionChanged.connect(self.selection_changed_steel)
        steel_layout.addWidget(self.table_steel)

        default_element = self._section.list_of_steel[0]
        self.add_an_element_in_the_steel_table(row_number=0, new_element=default_element)
        layout.addLayout(steel_layout)

    def load_layout_steel_buttons(self, layout: QVBoxLayout):
        layout_buttons = QHBoxLayout()
        layout.addLayout(layout_buttons)
        layout_buttons.addWidget(QLabel(MenuNames.label_steel))
        layout_buttons.addWidget(self.button_plus_steel)
        self.button_plus_steel.clicked.connect(self.plus_an_element_of_steel)
        layout_buttons.addWidget(self.button_minus_steel)
        self.button_minus_steel.clicked.connect(self.minus_an_element_of_steel)
        self.button_minus_steel.setEnabled(False)

    def load_layout_draw_section_diagram(self, section_layout: QVBoxLayout, diagram_layout):
        section_layout.addWidget(self.label_section_canvas)
        diagram_layout.addWidget(self.label_diagram_canvas)
        self.painter_section = QtGui.QPainter(self.canvas_section)
        self.painter_diagram = QtGui.QPainter(self.canvas_diagram)

    def make_scale_for_section(self) -> float | None:
        """returns scale x , y"""
        b, h = self._section.get_b_h_max()
        if b <= 0 or h <= 0:
            return None
        if self._section.carbon.calculate_with_carbon:
            h += self._section.carbon.z
        if self._section.addition_concrete.calculate_with_top_plate:
            h += self._section.addition_concrete.h
        b_c = variables_the_program.Menus.b_left_side
        h_c = variables_the_program.Menus.h_top
        return min(b_c / b * Menus.scale_canvas_section,
                   h_c / h * Menus.scale_canvas_section)

    def plus_an_element_of_concrete(self):
        self.button_minus_concrete.setEnabled(True)
        new_element = self._section.add_copy_of_last_element_and_return_it(type_of_section=MaterialVariables.concrete)
        b, h = self._section.get_b_h_max()
        self._section.addition_concrete.section.y0 = h
        self.update_the_concrete_table()


    def update_the_concrete_table(self, new_list_of_concrete_sections: list[AConcreteSection] = None):

        n = len(self._section.list_of_concrete_sections)
        for row_i in range(n):
            self.table_concrete.removeRow(0)
        row_i = 0
        if new_list_of_concrete_sections:
            self._section.list_of_concrete_sections = new_list_of_concrete_sections
        for section_i in reversed(self._section.list_of_concrete_sections):
            self.add_an_element_in_the_concrete_table(row_number=row_i, new_element=section_i)
            row_i += 1
        #   buttons + -
        if len(self._section.list_of_concrete_sections) > 1:
            self.button_minus_concrete.setEnabled(True)
        else:
            self.button_minus_concrete.setEnabled(False)
        if new_list_of_concrete_sections is None:
            return None
        concrete = new_list_of_concrete_sections[0].concrete.name_of_class
        index = MaterialVariables.concrete_class.index(concrete)
        self.combobox_objects_concrete_general.setCurrentIndex(index)
        self.draw_date_and_results()
        return None

    def minus_an_element_of_concrete(self):
        if len(self._section.list_of_concrete_sections) == 2:
            self.button_minus_concrete.setEnabled(False)
        self._section.remove_last_element(type_of_section=MaterialVariables.concrete)
        row = 0
        self.table_concrete.removeRow(row)
        b, h = self._section.get_b_h_max()
        self._section.addition_concrete.section.y0 = h
        self.draw_date_and_results()

    def add_an_element_in_the_concrete_table(self, row_number: int, new_element: AConcreteSection):
        self.table_concrete.insertRow(row_number)
        Menus.table_insert = True
        bo, bu, y0, h = new_element.get_bo_bu_y0_h()
        # b0
        self.table_concrete.setItem(row_number, 0, QTableWidgetItem(str(bu)))
        # bu
        self.table_concrete.setItem(row_number, 1, QTableWidgetItem(str(bo)))
        # h
        self.table_concrete.setItem(row_number, 2, QTableWidgetItem(str(h)))
        Menus.table_insert = False
        self.draw_date_and_results()

    def draw_date_and_results(self):
        self.draw_all()

        if not self._section.is_calculated:
            self.slider.setEnabled(False)
            return None
        self.make_results_enabled()
        return None

    def make_results_enabled(self):
        self.slider.setEnabled(True)
        self._m_max = float(list(self._section.result.keys())[-1])
        self.label_m_lim.setText(str(round(self._m_max, 2)))
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)

        self.draw_label_slider()

        # for slider label
        self.painter_slider.end()
        self.label_for_slider.setPixmap(self.canvas_slider)

    def draw_results(self):
        self.draw_stress_and_deformation(mi=self._mi)

    def draw_all(self) -> None:
        scale = self.make_scale_for_section()  # scale section
        if scale is None:
            return None
        # clear all
        # canvas section
        self.canvas_section = self.label_section_canvas.pixmap()
        self.canvas_section.fill(Qt.GlobalColor.black)
        self.painter_section = QtGui.QPainter(self.canvas_section)
        # canvas diagram
        self.canvas_diagram = self.label_diagram_canvas.pixmap()
        self.canvas_diagram.fill(Qt.GlobalColor.black)
        self.painter_diagram = QtGui.QPainter(self.canvas_diagram)

        # draw section
        if self._section.carbon.calculate_with_carbon:
            z = self._section.carbon.z
        elif self._section.addition_concrete.calculate_with_top_plate:
            z = -0.5*self._section.addition_concrete.h
        else:
            z = 0
        self.draw_concrete(scale=scale, z=z)
        self.draw_steel(scale=scale, z=z)
        if self._section.carbon.calculate_with_carbon:
            y = get_y0(section=self._section, scale=scale)
            self.draw_carbon_or_a_line_of_steel(y = y, scale=scale, area=self._section.carbon.area)
        if self._section.addition_concrete.calculate_with_top_plate:
            self.draw_addition_plate(scale=scale, z=z)
        self.draw_normal_force(scale=scale, z=z)

        self.draw_diagram_canvas()

        self.draw_results()

        # end all, send pictures
        # for sections
        self.painter_section.end()
        self.label_section_canvas.setPixmap(self.canvas_section)

        # for diagram
        self.painter_diagram.end()
        self.label_diagram_canvas.setPixmap(self.canvas_diagram)
        return None

    def draw_diagram_canvas(self):
        board = variables_the_program.Menus.board_canvas_diagram
        self.draw_all_diagrams_for_concrete(board=board)
        self.draw_all_diagrams_for_steel_and_carbon(board=board)

    def draw_all_diagrams_for_concrete(self, board: int | float):
        # diagrams for concrete
        y = variables_the_program.Menus.h_top / 2
        name_axes = Names.axes_concrete
        list_of_diagrams = [self._section.get_graph_for_concrete()]
        max_values = self._section.max_x_y_for_concrete
        scale_x_y = get_scale_x_y_for_diagram(max_values=max_values, board=board)
        self.draw_list_of_diagram_on_the_canvas(board=board, y0=y, name_axes=name_axes,
                                                list_of_diagrams=list_of_diagrams,
                                                scale_x_y=scale_x_y)

    def draw_all_diagrams_for_steel_and_carbon(self, board: int | float):
        y = variables_the_program.Menus.h_top
        name_axes = Names.axes_steel
        list_of_diagrams: list = self._section.get_graph_for_steel()

        # for carbon
        if self._section.carbon.calculate_with_carbon:
            diagram_carbon = self._section.get_graph_for_carbon()
            list_of_diagrams.append(diagram_carbon)
        max_values = self._section.max_x_y_for_steel
        scale_x_y = get_scale_x_y_for_diagram(max_values=max_values, board=board)
        self.draw_list_of_diagram_on_the_canvas(board=board, y0=y, name_axes=name_axes,
                                                list_of_diagrams=list_of_diagrams,
                                                scale_x_y=scale_x_y)

    def draw_list_of_diagram_on_the_canvas(self, board: int, y0: float,
                                           name_axes: tuple[str], list_of_diagrams: list,
                                           scale_x_y: tuple[float, float]):
        # draw axe
        pen = QtGui.QPen(MyColors.concrete_boards, PenThicknessToDraw.axis)
        self.painter_diagram.setPen(pen)
        brush = QtGui.QBrush(MyColors.axis)
        self.painter_diagram.setBrush(brush)
        # axes
        self.draw_axis_for_diagram(board=board, y00=y0, name_axes=name_axes)
        # diagrams
        for diagram in list_of_diagrams:
            self.draw_a_diagram_for_a_section(board=board, y0=y0, diagram=diagram, scale_x_y=scale_x_y)

    def draw_a_diagram_for_a_section(self, board: int, y0: float, diagram: DiagramToDraw,
                                     scale_x_y: tuple[float, float]):
        x_ = board
        y_ = y0 - board
        self.draw_lines_and_text_for_a_diagram(diagram=diagram, x_=x_, y_=y_, scale_x_y=scale_x_y)
        x0 = y0 = 0
        pen = QtGui.QPen(diagram.color, PenThicknessToDraw.graph_diagram)
        self.painter_diagram.setPen(pen)
        for i, x_y in enumerate(diagram.coordinates):
            if i == 0:
                x0, y0 = x_y
                continue
            self.painter_diagram.drawLine(int(x_ + x0 * scale_x_y[0]), int(y_ - y0 * scale_x_y[1]),
                                          int(x_ + x_y[0] * scale_x_y[0]), int(y_ - x_y[1] * scale_x_y[1]))
            x0, y0 = x_y

    def draw_lines_and_text_for_a_diagram(self, diagram: DiagramToDraw, x_: float, y_: float,
                                          scale_x_y: tuple[float, float]):
        shift_x = 15
        shift_y = 5
        # important coordinates
        pen = QtGui.QPen(MyColors.addition_lines, PenThicknessToDraw.addition_lines_for_diagram)
        pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        self.painter_diagram.setPen(pen)
        brush = QtGui.QBrush(MyColors.addition_lines)
        self.painter_diagram.setBrush(brush)
        # lines
        x1_y1, x2_y2 = diagram.important_coordinate
        x1, y1 = x1_y1
        x2, y2 = x2_y2

        self.painter_diagram.drawLine(int(x_), int(y_ - y1 * scale_x_y[1]),
                                      int(x_ + x1 * scale_x_y[0]), int(y_ - y1 * scale_x_y[1]))
        self.painter_diagram.drawLine(int(x_ + x1 * scale_x_y[0]), int(y_ - y1 * scale_x_y[1]),
                                      int(x_ + x1 * scale_x_y[0]), int(y_))
        self.painter_diagram.drawLine(int(x_), int(y_ - y2 * scale_x_y[1]),
                                      int(x_ + x2 * scale_x_y[0]), int(y_ - y2 * scale_x_y[1]))
        self.painter_diagram.drawLine(int(x_ + x2 * scale_x_y[0]), int(y_ - y2 * scale_x_y[1]),
                                      int(x_ + x2 * scale_x_y[0]), int(y_))
        # text x
        self.painter_diagram.drawText(QPoint(int(x_ + x1 * scale_x_y[0] - shift_x),
                                             int(y_ - shift_y)), str(round(x1, 4)))
        self.painter_diagram.drawText(QPoint(int(x_ + x2 * scale_x_y[0] - shift_x),
                                             int(y_ - shift_y)), str(round(x2, 4)))
        # text y
        self.painter_diagram.drawText(QPoint(int(x_ - shift_x),
                                             int(y_ - y1 * scale_x_y[1] - shift_y)), str(round(y1, 2)))
        if y1 == y2:
            return None
        self.painter_diagram.drawText(QPoint(int(x_ - shift_x),
                                             int(y_ - y2 * scale_x_y[1] - shift_y)), str(round(y2, 2)))
        return None

    def draw_axis_for_diagram(self, board: int, y00: float, name_axes: tuple[str]):
        # horizontal axis
        x0 = int(board / 2)
        y0 = int(y00 - board)
        x1 = int(Menus.b_center - board / 2)
        y1 = y0
        self.painter_diagram.drawLine(x0, y0, x1, y1)
        self.painter_diagram.drawText(QPoint(int(x1 - board * 0.8), int(y0 + board / 2)), name_axes[0])

        # vertical axis
        x0 = int(board)
        y0 = int(y00 - board / 2)
        x1 = x0
        y1 = int(y00 - Menus.h_top / 2 + board)
        self.painter_diagram.drawLine(x0, y0, x1, y1)
        self.painter_diagram.drawText(QPoint(int(x0 - board * 0.8), int(y1 - board * 0.1)), list(name_axes)[1])

    def draw_concrete(self, scale: float, z: float):
        # draw all _concrete sections
        pen = QtGui.QPen(MyColors.concrete_boards, PenThicknessToDraw.boards)
        self.painter_section.setPen(pen)
        brush = QtGui.QBrush(MyColors.concrete)
        for section in self._section.list_of_concrete_sections:
            self.draw_a_concrete_section(section=section, scale=scale, brush=brush, z=z)
        # draw y axe
        x0 = Menus.b_left_side * 0.5
        y0 = get_y0(section=self._section, scale=scale)
        y1 = Menus.h_top - y0
        pen = QtGui.QPen(MyColors.axis, PenThicknessToDraw.axis)
        self.painter_section.setPen(pen)
        self.painter_section.drawLine(int(x0), int(y0), int(x0), int(y1))

    def draw_addition_plate(self, scale: float, z: float):
        """draw the addition plate """

        # draw the concrete
        pen = QtGui.QPen(MyColors.concrete_addition_plate, PenThicknessToDraw.boards)
        self.painter_section.setPen(pen)
        brush = QtGui.QBrush(MyColors.concrete_addition)
        section = self._section.addition_concrete.section
        self.draw_a_concrete_section(section=section, scale=scale, brush=brush, z=z)

        # draw the steel
        steel = self._section.addition_concrete.steel
        y0 = get_y0(section=self._section, scale=scale)
        y = y0 - (self._section.addition_concrete.steel.steel_line._y + z) * scale
        self.draw_carbon_or_a_line_of_steel(y=y, area=steel.area, color=steel.color, scale=scale)

    def draw_normal_force(self, scale: float, z):
        pen = QtGui.QPen(MyColors.normal_force, PenThicknessToDraw.boards)
        self.painter_section.setPen(pen)
        if self._section.normal_force == 0:
            return None
        length = Menus.normal_force_length
        h = int(Menus.normal_force_height / 2)
        y = int(Menus.h_top * 0.5 * (1 + Menus.scale_canvas_section) - (self._section.eccentricity * 100 + z) * scale)

        x0 = int(Menus.b_left_side / 2)
        if self._section.normal_force < 0:
            self.painter_section.drawLine(x0, y, x0 - length, y)
            self.painter_section.drawLine(x0, y, int(x0 - length / 2), y + h)
            self.painter_section.drawLine(x0, y, int(x0 - length / 2), y - h)
        else:
            self.painter_section.drawLine(x0, y, x0 + length, y)
            self.painter_section.drawLine(x0, y, int(x0 + length / 2), y + h)
            self.painter_section.drawLine(x0, y, int(x0 + length / 2), y - h)
        return None

    def draw_label_slider(self):
        self.canvas_slider.fill(MyColors.label_slider_background)
        self.painter_slider = QtGui.QPainter(self.canvas_slider)
        pen = QtGui.QPen(MyColors.label_slider_lines, PenThicknessToDraw.axis)
        self.painter_slider.setPen(pen)
        self.label_for_slider.setPixmap(self.canvas_slider)
        if self._m_max == 0:
            return None
        for m in self._section.result.keys():
            x = int(m / self._m_max * Menus.sliders_width)
            self.painter_slider.drawLine(x, 0, x, Menus.slider_label_height)
        return None

    def draw_a_concrete_section(self, section: AConcreteSection, scale: float, z: float,
                                brush: QtGui.QBrush = QtGui.QBrush(QColor(50, 50, 50))):
        bo, bu, y0, h = section.get_bo_bu_y0_h()
        x0 = Menus.b_left_side * 0.5 - bu * scale * 0.5
        y01 = get_y0(section=self._section, scale=scale) - (y0 + z) * scale

        polygon = QPolygonF()
        polygon.append(QPoint(x0, y01))
        polygon.append(QPoint(x0 + bu * scale, y01))
        x1 = Menus.b_left_side * 0.5 + bo * scale * 0.5
        y1 = y01 - h * scale
        polygon.append(QPoint(x1, y1))
        polygon.append(QPoint(x1 - bo * scale, y1))

        self.draw_a_polygon(polygon=polygon, brush=brush)

    def draw_a_steel_section(self, section: ASteelLine, scale: float, z:float):
        color = QColor(*section.color_rgba)
        brush = QtGui.QBrush(color)
        self.painter_section.setBrush(brush)
        d, y, n, m, steel, s0 = section.get_d_y_n_m_steel_s0()
        b = self._section.get_b_for_y(y=y)
        t = b / n * scale  # space between steel
        r = ((d / 20) ** 2 * m) ** 0.5  # radius cm
        d = r * scale * 2

        y = get_y0(section=self._section, scale=scale) - (y + z) * scale - d / 2
        x = Menus.b_left_side * 0.5 - b * 0.5 * scale - d / 2 + t / 2
        for k in range(int(n)):
            self.painter_section.drawEllipse(x, y, d, d)
            x += t

    def draw_carbon_or_a_line_of_steel(self, y: float, area: float,
                                       scale: float, color: QColor = MyColors.carbon):
        brush = QtGui.QBrush(color)
        self.painter_section.setBrush(brush)
        b = self._section.get_b_bottom() * 0.8
        if b == 0:
            b = 0.1
        a = area / b
        y -= a / 2 * scale
        x = Menus.b_left_side * 0.5 - b / 2 * scale
        self.painter_section.drawRect(x, int(y), b * scale, a * scale)

    def draw_steel(self, scale: float, z: float):
        pen = QtGui.QPen(MyColors.concrete_boards, PenThicknessToDraw.steel_section)
        self.painter_section.setPen(pen)
        for section in self._section.list_of_steel:
            self.draw_a_steel_section(section=section, scale=scale, z=z)

    def draw_a_polygon(self, polygon: QPolygonF, brush: QtGui.QBrush = QtGui.QBrush(QColor(50, 50, 50))):
        self.painter_section.setBrush(brush)
        self.painter_section.drawPolygon(polygon)

    def plus_an_element_of_steel(self):
        self.button_minus_steel.setEnabled(True)
        self._section.add_copy_of_last_element_and_return_it(type_of_section=MaterialVariables.steel)
        self.update_the_steel_table()

    def update_additional_plate(self, new_list_of_add_plate: dict):

        calculate_with_add_plate: bool = new_list_of_add_plate['to_calculate'] if 'to_calculate' in new_list_of_add_plate else False
        self.checkbox_addition_top_plate.setChecked(calculate_with_add_plate)
        if not 'concrete' in new_list_of_add_plate:
            return None
        concrete_section = new_list_of_add_plate['concrete']
        concrete_class = concrete_section['concrete_class']
        index = MaterialVariables.concrete_class.index(concrete_class)
        self.combobox_addition_concrete.setCurrentIndex(index)
        b = concrete_section['b']
        h = concrete_section['h']
        self.line_edit_b.setText(str(b))
        self.line_edit_h.setText(str(h))

        Menus.table_insert = True
        self.table_additional_concrete.setRowCount(0)
        self.table_additional_concrete.insertRow(0)
        if "steel" in new_list_of_add_plate:
            steel_dict = new_list_of_add_plate['steel']
        else:
            return None
        try:
            area = float(steel_dict['area'])
            self._section.addition_concrete.steel.area = area
            z = float(steel_dict['z'])
            self._section.addition_concrete.steel.z = z
            m_int = float(new_list_of_add_plate['m_int'])
            self._section.addition_concrete.m_int = m_int
            steel_name = steel_dict['steel_class']
            self._section.addition_concrete.steel_name =steel_name
        except Exception as inst:
            print(type(inst))
            return None
        # A, cm2
        self.table_additional_concrete.setItem(0, 0, QTableWidgetItem(str(self._section.addition_concrete.steel.area)))
        # typ, cm2
        combobox_add_steel = QComboBox()
        steel_name = self._section.addition_concrete.steel_name
        for steel_name_i in MaterialVariables.steel_for_concrete:
            combobox_add_steel.addItem(steel_name_i)
        index = MaterialVariables.steel_for_concrete.index(steel_name)
        combobox_add_steel.setCurrentIndex(index)
        combobox_add_steel.currentIndexChanged.connect(self.change_index_of_combobox_addition_steel)
        self.table_additional_concrete.setCellWidget(0, 1, combobox_add_steel)
        # z, cm
        self.table_additional_concrete.setItem(0, 2, QTableWidgetItem(str(self._section.addition_concrete.steel.z)))
        # m_int, kNm
        self.table_additional_concrete.setItem(0, 3, QTableWidgetItem(str(self._section.addition_concrete.m_int)))
        Menus.table_insert = False
        self.draw_date_and_results()

        return None


    def update_carbon(self, new_list_of_carbone: dict):
        calculate_with_carbon = new_list_of_carbone['calculate_with_carbon']
        self.checkbox_carbon.setChecked(calculate_with_carbon)

        Menus.table_insert = True
        self.table_carbon.setRowCount(0)
        self.table_carbon.insertRow(0)
        try:
            area = float(new_list_of_carbone['area'])
            self._section.carbon.area = area
            z = float(new_list_of_carbone['z'])
            self._section.carbon.z = z
            m_int = float(new_list_of_carbone['m_int'])
            self._section.carbon.m_int = m_int
            carbon_name = new_list_of_carbone['type']
            self._section.carbon.carbon_class = carbon_name
        except Exception as inst:
            print(type(inst))
            return None
        # A, cm2
        self.table_carbon.setItem(0, 0, QTableWidgetItem(str(self._section.carbon.area)))
        # typ, cm2
        combobox_carbon = QComboBox()
        carbon_name = self._section.carbon.carbon_class
        for carbon_name_i in MaterialVariables.carbon_class:
            combobox_carbon.addItem(carbon_name_i)
        index = MaterialVariables.carbon_class.index(carbon_name)
        combobox_carbon.setCurrentIndex(index)
        combobox_carbon.currentIndexChanged.connect(self.change_index_of_combobox_carbon)
        self.table_carbon.setCellWidget(0, 1, combobox_carbon)
        # z, cm
        self.table_carbon.setItem(0, 2, QTableWidgetItem(str(self._section.carbon.z)))
        # m_int, kNm
        self.table_carbon.setItem(0, 3, QTableWidgetItem(str(self._section.carbon.m_int)))
        Menus.table_insert = False
        self.draw_date_and_results()
        return None

    def update_the_steel_table(self, new_list_of_steel: list[ASteelLine] = None):
        n = len(self._section.list_of_steel)
        for row_i in range(n):
            self.table_steel.removeRow(0)
        if new_list_of_steel:
            self._section.list_of_steel = new_list_of_steel
        row_i = 0
        for section_i in reversed(self._section.list_of_steel):
            self.add_an_element_in_the_steel_table(row_number=row_i, new_element=section_i)
            row_i += 1
        # + - buttons
        if n > 1:
            self.button_minus_steel.setEnabled(True)
        self.draw_date_and_results()

    def minus_an_element_of_steel(self):
        if len(self._section.list_of_steel) == 2:
            self.button_minus_steel.setEnabled(False)
        self._section.remove_last_element(type_of_section=MaterialVariables.steel)
        row = 0
        self.table_steel.removeRow(row)
        del self.list_of_combobox_steel[row]
        self.draw_date_and_results()

    def add_an_element_in_the_steel_table(self, row_number: int, new_element: ASteelLine):
        self.table_steel.insertRow(row_number)
        Menus.table_insert = True
        # Nr
        label = QLabel(str(row_number))
        random_color: str = new_element.color_str
        color_str = "QLabel { background-color : " + random_color + " }"
        label.setStyleSheet(color_str)
        self.table_steel.setCellWidget(row_number, 0, label)
        d, y, n, m, steel, s0 = new_element.get_d_y_n_m_steel_s0()
        # d
        self.table_steel.setItem(row_number, 1, QTableWidgetItem(str(d)))
        # m
        self.table_steel.setItem(row_number, 2, QTableWidgetItem(str(m)))
        # n
        self.table_steel.setItem(row_number, 3, QTableWidgetItem(str(n)))
        # y
        self.table_steel.setItem(row_number, 4, QTableWidgetItem(str(y)))
        # s0
        self.table_steel.setItem(row_number, 6, QTableWidgetItem(str(s0)))

        self.list_of_combobox_steel.append(QComboBox())
        steel_name = steel.name_of_class
        # steel
        for steel_name_i in MaterialVariables.steel_for_concrete:
            self.list_of_combobox_steel[-1].addItem(steel_name_i)
        # carbon
        for carbon_name_i in MaterialVariables.carbon_class:
            self.list_of_combobox_steel[-1].addItem(carbon_name_i)
        if steel_name in MaterialVariables.steel_for_concrete:
            index = MaterialVariables.steel_for_concrete.index(steel_name)
        elif steel_name in MaterialVariables.carbon_class:
            index = MaterialVariables.carbon_class.index(steel_name) + len(MaterialVariables.steel_for_concrete)
        else:
            index = 0
        self.list_of_combobox_steel[-1].setCurrentIndex(index)
        row_number_in_list = len(self._section.list_of_steel) - row_number - 1
        self.list_of_combobox_steel[-1].currentIndexChanged.connect(
            partial(self.change_index_of_combobox_steel, row_number_in_list))
        self.table_steel.setCellWidget(row_number, 5, self.list_of_combobox_steel[-1])
        Menus.table_insert = False
        self.draw_date_and_results()

    def change_index_of_combobox_steel(self, row_number: int, index: int):
        steel_line = self._section.list_of_steel[row_number]
        if index < len(MaterialVariables.steel_for_concrete):
            new_steel_name = MaterialVariables.steel_for_concrete[index]
        else:
            index -= len(MaterialVariables.steel_for_concrete)
            new_steel_name = MaterialVariables.carbon_class[index]
        steel_line.steel = new_steel_name
        self.draw_date_and_results()

    def draw_stress_and_deformation(self, mi: float = 0):
        result: Result = self.make_result_for_mi(mi=mi)
        if result is None:
            return None
        self.label_current_normal_force_n_i.setText(str(round(result.dn, 2)))
        self.draw_the_graph(result=result)
        return None

    def make_result_for_mi(self, mi: float) -> Result | None:
        """the function interpolate new graphic for current m_i"""
        if mi == 0:
            return None
        if mi <= list(self._section.result.keys())[0]:
            m_i = list(self._section.result.keys())[0]
            return self._section.result[m_i]
        if mi >= list(self._section.result.keys())[-1]:
            m_i = list(self._section.result.keys())[-1]
            return self._section.result[m_i]
        for i in range(len(self._section.result)):
            m_i = list(self._section.result.keys())[i]
            m1_plus_1 = list(self._section.result.keys())[i + 1]
            if m_i <= mi < m1_plus_1:
                result_1 = self._section.result[m_i]
                result_2 = self._section.result[m1_plus_1]
                return make_intermediate_result_for_the_graphic(mi=mi, result_1=result_1, result_2=result_2)
        return None

    def draw_the_graph(self, result: Result):
        graph: GeneralGraphicForResult = result.graph
        scale_concrete, scale_steel = self.make_scales_for_stress()
        if self._section.carbon.calculate_with_carbon:
            z = self._section.carbon.z
        elif self._section.addition_concrete.calculate_with_top_plate:
            z = -0.5*self._section.addition_concrete.h
        else:
            z = 0
        x0_y0 = [Menus.b_left_side * 0.5, get_y0(section=self._section, scale=scale_concrete[1])]
        x0_y0_z = [x0_y0[0], x0_y0[1] - z * scale_concrete[1]]

        # draw concrete
        for graph_concrete in graph.graphic_for_concrete:
            self.draw_a_graph_concrete(graph_concrete=graph_concrete,
                                       scale_concrete=scale_concrete, x0_y0=x0_y0_z)

        # draw steel
        for graph_steel in graph.graphic_for_steel:
            draw_a_graph_steel(self.painter_section, graph_steel=graph_steel,
                               scale_steel=scale_steel, x0_y0=x0_y0_z)

        # draw carbon
        if self._section.carbon.calculate_with_carbon:
            x0_y0_z2 = x0_y0[0], x0_y0[1] + z * scale_concrete[1]
            draw_a_graph_steel(self.painter_section, graph_steel=graph.graphic_for_carbon,
                               scale_steel=scale_steel, x0_y0=x0_y0_z2)

        # draw strain
        e_top = result.e_top
        e_bottom = result.e_bottom
        self.draw_strains_for_section_canvas(x0_y0=x0_y0_z, e_top=e_top, e_bottom=e_bottom)
        if self._section.addition_concrete.calculate_with_top_plate:
            self.draw_strains_for_additional_plate(x0_y0=x0_y0_z, e_top=result.e_top_add_plate,
                                                   e_bottom=result.e_bottom_add_plate)
        self.draw_strains_for_diagram_canvas(result=result)

    def draw_strains_for_additional_plate(self, x0_y0: list[float], e_top: float, e_bottom: float) -> None:
        pen = QtGui.QPen(MyColors.strains_section, PenThicknessToDraw.strains_section)
        pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        self.painter_section.setPen(pen)
        x_max, _ = self._section.max_x_y_for_steel
        _, y_max = self._section.get_b_h_max()
        b_c = variables_the_program.Menus.b_left_side
        scale_x = b_c / x_max * Menus.scale_canvas_section * 0.5*0.8
        scale_y = self.make_scale_for_section()
        # coordinates at the bottom
        x0 = int(x0_y0[0] + e_bottom * scale_x)
        y0 = int(x0_y0[1] - y_max * scale_y)
        # coordinates above
        x1 = int(x0_y0[0] + e_top * scale_x)
        y1 = int(x0_y0[1] - (y_max + self._section.addition_concrete.h) * scale_y)
        self.painter_section.drawLine(x0, y0, x1, y1)
        # text at the bottom
        text_bottom = str(round(e_bottom, 5))
        self.painter_section.drawText(x0, y0 + 12, text_bottom)
        # text at the top
        text_top = str(round(e_top, 5))
        self.painter_section.drawText(x1, y1 - 5, text_top)

    def draw_strains_for_section_canvas(self, x0_y0: list[float], e_top: float, e_bottom: float) -> None:
        pen = QtGui.QPen(MyColors.strains_section, PenThicknessToDraw.strains_section)
        pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        self.painter_section.setPen(pen)
        x_max, _ = self._section.max_x_y_for_steel
        _, y_max = self._section.get_b_h_max()
        b_c = variables_the_program.Menus.b_left_side
        scale_x = b_c / x_max * Menus.scale_canvas_section * 0.5*0.8
        scale_y = self.make_scale_for_section()
        # coordinates at the bottom
        x0 = int(x0_y0[0] + e_bottom * scale_x)
        y0 = int(x0_y0[1])
        # coordinates above
        x1 = int(x0_y0[0] + e_top * scale_x)
        if self._section.addition_concrete.calculate_with_top_plate:
            y1 = int(x0_y0[1] - (y_max + self._section.addition_concrete.h) * scale_y)
        else:
            y1 = int(x0_y0[1] - y_max * scale_y)
        self.painter_section.drawLine(x0, y0, x1, y1)
        # text at the bottom
        text_bottom = str(round(e_bottom, 5))
        self.painter_section.drawText(x0, y0 + 12, text_bottom)
        # text at the top
        text_top = str(round(e_top, 5))
        self.painter_section.drawText(x1, y1 - 5, text_top)

    def draw_strains_for_diagram_canvas(self, result: Result):
        self.draw_concrete_strain_and_stress_for_diagram_canvas(result=result)
        self.draw_steel_strain_and_stress_for_diagram_canvas(result=result)

    def draw_concrete_strain_and_stress_for_diagram_canvas(self, result: Result):
        # brush and pen
        pen = QtGui.QPen(MyColors.concrete_diagram, PenThicknessToDraw.graph_diagram)
        self.painter_diagram.setPen(pen)
        brush = QtGui.QBrush(QColor(0, 0, 0, 0))
        self.painter_diagram.setBrush(brush)
        # draw the point at the top with max ec, sc
        y = variables_the_program.Menus.h_top / 2
        max_values = self._section.max_x_y_for_concrete
        board = Menus.board_canvas_diagram
        scale_x_y = get_scale_x_y_for_diagram(max_values=max_values, board=board)
        x_ = board
        y_ = y - board
        ec = result.e_top
        sc = result.sc
        r = Menus.radius_for_diagram_strain_circles
        x = int(x_ + ec * scale_x_y[0])
        y = int(y_ - sc * scale_x_y[1])
        self.painter_diagram.drawEllipse(x - r, y - r, 2 * r, 2 * r)

    def draw_steel_strain_and_stress_for_diagram_canvas(self, result: Result):
        for graph in result.graph.graphic_for_steel:
            self.draw_concrete_strain_and_stress_for_diagram_canvas_for_a_steel(graph=graph)
        if self._section.carbon.calculate_with_carbon:
            self.draw_concrete_strain_and_stress_for_diagram_canvas_for_a_steel(graph=result.graph.graphic_for_carbon)

    def draw_concrete_strain_and_stress_for_diagram_canvas_for_a_steel(self, graph: ResultGraphSteel):
        # brush and pen
        if graph is None:
            return None
        pen = QtGui.QPen(graph.color, PenThicknessToDraw.graph_diagram)
        self.painter_diagram.setPen(pen)
        brush = QtGui.QBrush(QColor(0, 0, 0, 0))
        self.painter_diagram.setBrush(brush)
        # draw the point at the top with max es, ss
        y = variables_the_program.Menus.h_top
        max_values = self._section.max_x_y_for_steel
        board = Menus.board_canvas_diagram
        scale_x_y = get_scale_x_y_for_diagram(max_values=max_values, board=board)
        x_ = board
        y_ = y - board
        ec = abs(graph.es)
        sc = abs(graph.ss)
        r = Menus.radius_for_diagram_strain_circles
        x = int(x_ + ec * scale_x_y[0])
        y = int(y_ - sc * scale_x_y[1])
        self.painter_diagram.drawEllipse(x - r, y - r, 2 * r, 2 * r)
        return None

    def make_scales_for_stress(self) -> tuple[tuple[float, float | None], tuple[float, float | None]]:
        _, max_values_concrete = self._section.max_x_y_for_concrete
        _, max_values_steel = self._section.max_x_y_for_steel
        y_scale = self.make_scale_for_section()
        b_c = variables_the_program.Menus.b_left_side
        scale_for_concrete = b_c / max_values_concrete * Menus.scale_canvas_section * 0.5, y_scale
        scale_fo_steel = b_c / max_values_steel * Menus.scale_canvas_section * 0.5, y_scale
        return scale_for_concrete, scale_fo_steel

    def draw_a_graph_concrete(self, graph_concrete: list[ResultGraphConcrete], scale_concrete: tuple[float],
                              x0_y0: list[float]):
        self.draw_polygon_for_concrete(graph_concrete=graph_concrete,
                                       scale_concrete=scale_concrete, x0_y0=x0_y0)
        draw_lines_above_concrete_diagram(self.painter_section, graph_concrete=graph_concrete,
                                          scale_concrete=scale_concrete, x0_y0=x0_y0)

    def draw_polygon_for_concrete(self, graph_concrete: list[ResultGraphConcrete],
                                  scale_concrete: list[float], x0_y0: list[float]):
        polygon = make_polygon_to_draw_concrete(graph_concrete=graph_concrete,
                                                scale_concrete=scale_concrete, x0_y0=x0_y0)
        pen = QtGui.QPen(MyColors.concrete_diagram, PenThicknessToDraw.stress_concrete)
        self.painter_section.setPen(pen)
        brush = QtGui.QBrush(MyColors.concrete_diagram_polygon)
        self.painter_section.setBrush(brush)
        self.draw_a_polygon(polygon=polygon, brush=brush)


