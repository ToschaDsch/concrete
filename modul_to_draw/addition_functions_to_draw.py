from PySide6 import QtGui
from PySide6.QtCore import QPoint
from PySide6.QtGui import QPolygonF

from moduls_to_calculate.general_class_to_calculate import AllElementsOfTheSection
from variables.variables_for_material import Result, ResultGraphConcrete, ResultGraphSteel, GeneralGraphicForResult
from variables.variables_the_program import Menus, MyColors, PenThicknessToDraw


def make_intermediate_result_for_the_graphic(mi, result_1: Result,
                                             result_2: Result) -> Result | None:
    graphic_for_concrete = []
    m1 = result_1.moment
    m2 = result_2.moment

    # intermediate graphic for concrete
    if result_1 is None:
        return result_2
    if result_2 is None:
        return result_1
    if len(result_1.graph.graphic_for_concrete) != len(result_2.graph.graphic_for_concrete):
        graphic_for_concrete = result_1.graph.graphic_for_concrete
    else:
        for j in range(len(result_1.graph.graphic_for_concrete)):
            graph_for_one_element_i = []
            for i in range(len(result_1.graph.graphic_for_concrete[j])):
                graph_1: ResultGraphConcrete = result_1.graph.graphic_for_concrete[j][i]
                graph_2: ResultGraphConcrete = result_2.graph.graphic_for_concrete[j][i]
                ec = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=graph_1.ec, r2=graph_2.ec)
                yi = graph_1.yi
                sc = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=graph_1.sc, r2=graph_2.sc)
                graph_for_one_element_i.append(ResultGraphConcrete(ec=ec, yi=yi, sc=sc))
            graphic_for_concrete.append(graph_for_one_element_i)

    # intermediate graphic for steel
    graphic_for_steel = []
    for i in range(len(result_1.graph.graphic_for_steel)):
        graph_1: ResultGraphSteel = result_1.graph.graphic_for_steel[i]
        graph_2: ResultGraphSteel = result_2.graph.graphic_for_steel[i]
        es, yi, ss = get_es_yi_ss(mi=mi, m1=m1, m2=m2, graph_1=graph_1, graph_2=graph_2)
        graphic_for_steel.append(ResultGraphSteel(es=es, yi=yi, ss=ss, color=graph_1.color))

    # carbon
    if result_1.graph.graphic_for_carbon and result_2.graph.graphic_for_carbon:
        graph_1: ResultGraphSteel = result_1.graph.graphic_for_carbon
        graph_2: ResultGraphSteel = result_2.graph.graphic_for_carbon
        es, yi, ss = get_es_yi_ss(mi=mi, m1=m1, m2=m2, graph_1=graph_1, graph_2=graph_2)
        graphic_for_carbon = ResultGraphSteel(es=es, yi=yi, ss=ss, color=graph_1.color)
    else:
        graphic_for_carbon = ResultGraphSteel(es=0, yi=0, ss=0, color=MyColors.carbon_stress)

    graphic = GeneralGraphicForResult(graphic_for_concrete=graphic_for_concrete,
                                      graphic_for_steel=graphic_for_steel, graphic_for_carbon=graphic_for_carbon)
    # dates for result
    normal_force = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.normal_force, r2=result_2.normal_force)
    e_top = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.e_top, r2=result_2.e_top)
    e_bottom = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.e_bottom, r2=result_2.e_bottom)
    dn = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.dn, r2=result_2.dn)
    sc = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.sc, r2=result_2.sc)
    e_top_add_plate = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.e_top_add_plate, r2=result_2.e_top_add_plate)
    e_bottom_add_plate = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=result_1.e_bottom_add_plate, r2=result_2.e_bottom_add_plate)
    result = Result(normal_force=normal_force, moment=mi, graph=graphic, e_top=e_top, e_bottom=e_bottom, dn=dn, sc=sc,
                    e_top_add_plate=e_top_add_plate, e_bottom_add_plate=e_bottom_add_plate)
    return result

def get_es_yi_ss(mi, m1, m2, graph_1, graph_2):
    es = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=graph_1.es, r2=graph_2.es)
    yi = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=graph_1.yi, r2=graph_2.yi)
    ss = interpolate_for_graph(mi=mi, m1=m1, m2=m2, r1=graph_1.ss, r2=graph_2.ss)
    return es, yi, ss

def interpolate_for_graph(mi: float, m1: float, m2: float, r1: float, r2: float) -> float:
    if m2 - m1 == 0:
        return r1
    return (r2 - r1) * (mi - m1) / (m2 - m1) + r1


def get_scale_x_y_for_diagram(board: float, max_values: tuple[float, float]) -> tuple[float, float]:
    b = Menus.b_center - 2 * board
    h = Menus.h_top * 0.5 - 3 * board

    return b / max_values[0], h / max_values[1]


def make_polygon_to_draw_concrete(graph_concrete: list[ResultGraphConcrete],
                                  scale_concrete: list[float], x0_y0: list[float]) -> QPolygonF:
    polygon = QPolygonF()
    flag = 0  # first element with s > 0
    n = len(graph_concrete) - 1
    dx = graph_concrete[n].sc - graph_concrete[n - 1].sc
    dy = graph_concrete[n].yi - graph_concrete[n - 1].yi

    for i, lines in enumerate(graph_concrete):
        yi = lines.yi
        sc = lines.sc
        if sc == 0:
            continue
        if flag == 0 and i != n:
            x0 = int(x0_y0[0])
            y0 = int(x0_y0[1] - (yi - dy / 2) * scale_concrete[1])
            polygon.append(QPoint(x0, y0))
            s_ = 0.5 * (3 * sc - graph_concrete[i + 1].sc)
            if s_ < 0:
                s_ = 0
            polygon.append(QPoint(int(x0 + s_ * scale_concrete[0]), y0))
            flag = 1
        xi = int(x0_y0[0] + sc * scale_concrete[0])
        yi = int(x0_y0[1] - yi * scale_concrete[1])
        polygon.append(QPoint(xi, yi))

    xn = int(x0_y0[0] + (graph_concrete[n].sc + dx / 2) * scale_concrete[0])
    yn = int(x0_y0[1] - (graph_concrete[n].yi + dy / 2) * scale_concrete[1])
    polygon.append(QPoint(xn, yn))
    polygon.append(QPoint(int(x0_y0[0]), yn))
    return polygon


def draw_a_graph_steel(painter_section, graph_steel: ResultGraphSteel, scale_steel: tuple[float],
                       x0_y0: list[float]):
    if graph_steel is None:
        return None
    yi = graph_steel.yi
    ss = graph_steel.ss
    x0 = x0_y0[0]
    y0 = x0_y0[1] - yi * list(scale_steel)[1]
    x1 = x0_y0[0] + ss * scale_steel[0]

    pen = QtGui.QPen(graph_steel.color, PenThicknessToDraw.stress_steel)
    painter_section.setPen(pen)
    brush = QtGui.QBrush(graph_steel.color)
    painter_section.setBrush(brush)

    painter_section.drawLine(x0, y0, x1, y0)
    return None


def draw_polygon_for_concrete(self, graph_concrete: list[ResultGraphConcrete],
                              scale_concrete: list[float], x0_y0: list[float]):
    polygon = make_polygon_to_draw_concrete(graph_concrete=graph_concrete,
                                            scale_concrete=scale_concrete, x0_y0=x0_y0)
    pen = QtGui.QPen(MyColors.concrete_diagram, PenThicknessToDraw.stress_concrete)
    self.painter_section.setPen(pen)
    brush = QtGui.QBrush(MyColors.concrete_diagram_polygon)
    self.painter_section.setBrush(brush)
    self.draw_a_polygon(polygon=polygon, brush=brush)


def draw_lines_above_concrete_diagram(painter_section, graph_concrete: list[ResultGraphConcrete],
                                      scale_concrete: list[float], x0_y0: list[float]):
    pen = QtGui.QPen(MyColors.concrete_diagram, PenThicknessToDraw.stress_concrete)
    painter_section.setPen(pen)
    brush = QtGui.QBrush(MyColors.concrete_diagram)
    painter_section.setBrush(brush)
    for lines in graph_concrete:
        yi = lines.yi
        sc = lines.sc
        x0 = x0_y0[0]
        y0 = x0_y0[1] - yi * scale_concrete[1]
        x1 = x0_y0[0] + sc * scale_concrete[0]
        painter_section.drawLine(x0, y0, x1, y0)


def get_y0(section: AllElementsOfTheSection, scale: float) -> float:
    b, h = section.get_b_h_max()
    return Menus.h_top/2 + h/2 * scale
