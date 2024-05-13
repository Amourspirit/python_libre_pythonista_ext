from __future__ import annotations
from enum import Enum

import uno
from com.sun.star.chart2 import XChartDocument
from com.sun.star.sheet import XSpreadsheet
from com.sun.star.sheet import XSpreadsheetDocument

from ooodev.dialog.msgbox import MsgBox, MessageBoxType, MessageBoxButtonsEnum, MessageBoxResultsEnum
from ooodev.office.calc import Calc
from ooodev.office.chart2 import (
    Chart2,
    Chart2ControllerLock,
    Angle,
    DataPointLabelTypeKind,
    DataPointGeometry3DEnum,
    CurveKind,
    mEx,
)
from ooodev.utils.color import CommonColor
from ooodev.utils.file_io import FileIO
from ooodev.utils.gui import GUI
from ooodev.utils.kind.axis_kind import AxisKind
from ooodev.utils.kind.chart2_types import ChartTypes
from ooodev.utils.kind.data_point_lable_placement_kind import DataPointLabelPlacementKind
from ooodev.utils.lo import Lo
from ooodev.utils.props import Props
from ooodev.utils.type_var import PathOrStr

from ooo.dyn.awt.font_weight import FontWeight
from ooo.dyn.chart.time_increment import TimeIncrement
from ooo.dyn.chart.time_interval import TimeInterval
from ooo.dyn.chart.time_unit import TimeUnit
from ooo.dyn.chart2.axis_orientation import AxisOrientation
from ooo.dyn.chart2.axis_type import AxisType
from ooo.dyn.drawing.line_style import LineStyle


class ChartKind(str, Enum):
    AREA = "area"
    BAR = "bar"
    BUBBLE_LABELED = "bubble_labeled"
    COLUMN = "col"
    COLUMN_LINE = "col_line"
    COLUMN_MULTI = "col_multi"
    DONUT = "donut"
    HAPPY_STOCK = "happy_stock"
    LINE = "line"
    LINES = "lines"
    NET = "net"
    PIE = "pie"
    PIE_3D = "pie_3d"
    SCATTER = "scatter"
    SCATTER_LINE_ERROR = "scatter_line_error"
    SCATTER_LINE_LOG = "scatter_line_log"
    STOCK_PRICES = "stock_prices"
    DEFAULT = "default"
    DISPATCH = "dispatch"


class Chart2View:
    def __init__(self, data_fnm: PathOrStr, chart_kind: ChartKind, **kwargs) -> None:
        _ = FileIO.is_exist_file(data_fnm, True)
        self._data_fnm = FileIO.get_absolute_path(data_fnm)
        self._chart_kind = chart_kind
        so = kwargs.get("soffice", None)
        if so:
            _ = FileIO.is_exist_file(so, True)
            self._soffice = str(FileIO.get_absolute_path(so))
        else:
            self._soffice = None

    def main(self) -> None:
        opt = Lo.Options(verbose=True)
        if self._soffice:
            loader = Lo.load_office(Lo.ConnectPipe(soffice=self._soffice), opt=opt)
        else:
            loader = Lo.load_office(Lo.ConnectPipe(), opt=opt)

        try:
            doc = Calc.open_doc(fnm=self._data_fnm, loader=loader)
            GUI.set_visible(visible=True, doc=doc)
            Lo.delay(300)
            Calc.zoom_value(doc=doc, value=75)
            sheet = Calc.get_sheet(doc=doc, idx=0)

            chart_doc = None
            if self._chart_kind == ChartKind.AREA:
                chart_doc = self._area_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.BAR:
                chart_doc = self._bar_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.BUBBLE_LABELED:
                chart_doc = self._labeled_bubble_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.COLUMN:
                chart_doc = self._col_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.COLUMN_LINE:
                chart_doc = self._col_line_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.COLUMN_MULTI:
                chart_doc = self._multi_col_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.DONUT:
                chart_doc = self._donut_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.HAPPY_STOCK:
                chart_doc = self._happy_stock_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.LINE:
                chart_doc = self._line_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.LINES:
                chart_doc = self._lines_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.NET:
                chart_doc = self._net_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.PIE:
                chart_doc = self._pie_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.PIE_3D:
                chart_doc = self._pie_3d_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.SCATTER:
                chart_doc = self._scatter_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.SCATTER_LINE_ERROR:
                chart_doc = self._scatter_line_error_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.SCATTER_LINE_LOG:
                chart_doc = self._scatter_line_log_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.STOCK_PRICES:
                chart_doc = self._stock_prices_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.DEFAULT:
                chart_doc = self._default_chart(doc=doc, sheet=sheet)
            elif self._chart_kind == ChartKind.DISPATCH:
                self._default_dispatch(doc=doc, sheet=sheet)

            if chart_doc:
                Chart2.print_chart_types(chart_doc)

                template_names = Chart2.get_chart_templates(chart_doc)
                Lo.print_names(template_names, 1)

            Lo.delay(2000)
            msg_result = MsgBox.msgbox(
                "Do you wish to close document?",
                "All done",
                boxtype=MessageBoxType.QUERYBOX,
                buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
            )
            if msg_result == MessageBoxResultsEnum.YES:
                Lo.close_doc(doc=doc, deliver_ownership=True)
                Lo.close_office()
            else:
                print("Keeping document open")
        except Exception:
            Lo.close_office()
            raise

    def _col_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draw a column chart;
        # uses "Sneakers Sold this Month" table
        range_addr = Calc.get_address(sheet=sheet, range_name="A2:B8")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="C3",
            width=15,
            height=11,
            diagram_name=ChartTypes.Column.TEMPLATE_STACKED.COLUMN,
            chart_name="col_chart",
        )
        Calc.goto_cell(cell_name="A1", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A1"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A2"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="B2"))
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        return chart_doc

    def _multi_col_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a multiple column chart: 2D and 3D
        # uses "States with the Most Colleges and Universities by Type"
        range_addr = Calc.get_address(sheet=sheet, range_name="E15:G21")
        d_name = ChartTypes.Column.TEMPLATE_STACKED.COLUMN
        # d_name = ChartTypes.Column.TEMPLATE_PERCENT.COLUMN_DEEP_3D
        # d_name = ChartTypes.Column.TEMPLATE_PERCENT.COLUMN_FLAT_3D
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="A22",
            width=20,
            height=11,
            diagram_name=d_name,
            chart_name="multi_col_chart",
        )
        ChartTypes.Column.TEMPLATE_STACKED.COLUMN
        Calc.goto_cell(cell_name="A13", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E13"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E15"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="F14"))
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)

        # for the 3D versions
        # hide labels
        # Chart2.show_axis_label(chart_doc=chart_doc, axis_val=AxisKind.Z, idx=0, is_visible=False)
        # Chart2.set_chart_shape_3d(chart_doc=chart_doc, shape=DataPointGeometry3DEnum.CYLINDER)
        return chart_doc

    def _col_line_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a column+line chart
        # uses "States with the Most Colleges and Universities by Type"
        range_addr = Calc.get_address(sheet=sheet, range_name="E15:G21")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="B3",
            width=20,
            height=11,
            diagram_name=ChartTypes.ColumnAndLine.TEMPLATE_STACKED.COLUMN_WITH_LINE,
            chart_name="col_chart",
        )
        Calc.goto_cell(cell_name="A13", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E13"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E15"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="F14"))
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)
        return chart_doc

    def _bar_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # uses "Sneakers Sold this Month" table
        range_addr = Calc.get_address(sheet=sheet, range_name="A2:B8")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="B3",
            width=15,
            height=11,
            diagram_name=ChartTypes.Bar.TEMPLATE_STACKED.BAR,
            chart_name="bar_chart",
        )
        Calc.goto_cell(cell_name="A1", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A1"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A2"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="B2"))
        # rotate x-axis which is now the vertical axis
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        return chart_doc

    def _pie_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draw a pie chart, with legend and subtitle;
        # uses "Top 5 States with the Most Elementary and Secondary Schools"
        range_addr = Calc.get_address(sheet=sheet, range_name="E2:F8")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="B10",
            width=12,
            height=11,
            diagram_name=ChartTypes.Pie.TEMPLATE_DONUT.PIE,
            chart_name="pie_chart",
        )
        Calc.goto_cell(cell_name="A1", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E1"))
        Chart2.set_subtitle(chart_doc=chart_doc, subtitle=Calc.get_string(sheet=sheet, cell_name="F2"))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)
        return chart_doc

    def _pie_3d_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a 3D pie chart with rotation, label change
        # uses "Top 5 States with the Most Elementary and Secondary Schools"
        range_addr = Calc.get_address(sheet=sheet, range_name="E2:F8")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="B10",
            width=12,
            height=11,
            diagram_name=ChartTypes.Pie.TEMPLATE_3D.PIE_3D,
            chart_name="pie_chart_3d",
        )
        Calc.goto_cell(cell_name="A1", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E1"))
        Chart2.set_subtitle(chart_doc=chart_doc, subtitle=Calc.get_string(sheet=sheet, cell_name="F2"))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)

        # rotate around horizontal (x-axis) and vertical (y-axis)
        diagram = chart_doc.getFirstDiagram()
        Props.set(
            diagram,
            RotationHorizontal=0,  # -ve rotates bottom edge out of page; default is -60
            RotationVertical=-45,  # -ve rotates left edge out of page; default is 0 (i.e. no rotation)
        )
        # Props.show_obj_props("Diagram", diagram)

        # change all the data points to be bold white 14pt
        # ds = Chart2.get_data_series(chart_doc)
        # Lo.print(f"No. of data series: {len(ds)}")
        # Props.show_obj_props("Data Series 0", ds[0])
        # Props.set(ds[0], CharHeight=14.0, CharColor=CommonColor.WHITE, CharWeight=FontWeight.BOLD)

        props_lst = Chart2.get_data_points_props(chart_doc=chart_doc, idx=0)
        Lo.print(f"Number of data props in first data series: {len(props_lst)}")

        # change only the last data point to be bold white 14pt
        try:
            props = Chart2.get_data_point_props(chart_doc=chart_doc, series_idx=0, idx=0)
            Props.set(props, CharHeight=14.0, CharColor=CommonColor.WHITE, CharWeight=FontWeight.BOLD)
        except mEx.NotFoundError:
            Lo.print("No Properties found for chart.")
        return chart_doc

    def _donut_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a 3D donut chart with 2 rings
        # uses the "Annual Expenditure on Institutions" table
        range_addr = Calc.get_address(sheet=sheet, range_name="A44:C50")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="D43",
            width=15,
            height=11,
            diagram_name=ChartTypes.Pie.TEMPLATE_DONUT.DONUT,
            chart_name="donut_chart",
        )
        Calc.goto_cell(cell_name="A48", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A43"))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)
        subtitle = f'Outer: {Calc.get_string(sheet=sheet, cell_name="B44")}\nInner: {Calc.get_string(sheet=sheet, cell_name="C44")}'
        Chart2.set_subtitle(chart_doc=chart_doc, subtitle=subtitle)
        return chart_doc

        # Chart2.set_data_point_labels(chart_doc=chart_doc, label_type=DataPointLabelTypeKind.CATEGORY)

    def _area_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws an area (stacked) chart;
        # uses "Trends in Enrollment in Public Schools in the US" table
        range_addr = Calc.get_address(sheet=sheet, range_name="E45:G50")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="A52",
            width=16,
            height=11,
            diagram_name=ChartTypes.Area.TEMPLATE_STACKED.AREA,
            chart_name="area_chart",
        )
        Calc.goto_cell(cell_name="A43", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E43"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E45"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="F44"))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        return chart_doc

    def _line_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> None:
        # draw a line chart with data points, no legend;
        # uses "Humidity Levels in NY" table
        range_addr = Calc.get_address(sheet=sheet, range_name="A14:B21")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="D13",
            width=16,
            height=9,
            diagram_name=ChartTypes.Line.TEMPLATE_SYMBOL.LINE_SYMBOL,
            chart_name="line_chart",
        )
        Calc.goto_cell(cell_name="A1", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A13"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A14"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="B14"))

    def _lines_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draw a line chart with two lines;
        # uses "Trends in Expenditure Per Pupil"
        range_addr = Calc.get_address(sheet=sheet, range_name="E27:G39")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="A40",
            width=22,
            height=11,
            diagram_name=ChartTypes.Line.TEMPLATE_SYMBOL.LINE_SYMBOL,
            chart_name="lines_chart",
        )
        Calc.goto_cell(cell_name="A39", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E26"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E27"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title="Expenditure per Pupil")
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))

        # too crowded for data points
        Chart2.set_data_point_labels(chart_doc=chart_doc, label_type=DataPointLabelTypeKind.NONE)
        return chart_doc

    def _scatter_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # data from http://www.mathsisfun.com/data/scatter-xy-plots.html;
        # uses the "Ice Cream Sales vs Temperature" table
        range_addr = Calc.get_address(sheet=sheet, range_name="A110:B122")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="C109",
            width=16,
            height=11,
            diagram_name=ChartTypes.XY.TEMPLATE_LINE.SCATTER_SYMBOL,
            chart_name="scatter_chart",
        )
        Calc.goto_cell(cell_name="A104", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A109"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A110"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="B110"))
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))

        Chart2.calc_regressions(chart_doc)

        Chart2.draw_regression_curve(chart_doc=chart_doc, curve_kind=CurveKind.LINEAR)
        return chart_doc

    def _scatter_line_log_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draw a x-y scatter chart using log scaling
        # uses the "Power Function Test" table
        range_addr = Calc.get_address(sheet=sheet, range_name="E110:F120")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="A121",
            width=20,
            height=11,
            diagram_name=ChartTypes.XY.TEMPLATE_LINE.SCATTER_LINE_SYMBOL,
            chart_name="scatter_line_log_chart",
        )
        Calc.goto_cell(cell_name="A121", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E109"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E110"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="F110"))
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))

        # change x- and y- axes to log scaling
        x_axis = Chart2.scale_x_axis(chart_doc=chart_doc, scale_type=CurveKind.LOGARITHMIC)
        # Chart2.print_scale_data("x-axis", x_axis)
        _ = Chart2.scale_y_axis(chart_doc=chart_doc, scale_type=CurveKind.LOGARITHMIC)
        Chart2.draw_regression_curve(chart_doc=chart_doc, curve_kind=CurveKind.POWER)
        return chart_doc

    def _scatter_line_error_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws an x-y scatter chart with lines and y-error bars
        # uses the smaller "Impact Data - 1018 Cold Rolled" table
        # the example comes from "Using Descriptive Statistics.pdf"

        range_addr = Calc.get_address(sheet=sheet, range_name="A142:B146")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="F115",
            width=14,
            height=16,
            diagram_name=ChartTypes.XY.TEMPLATE_LINE.SCATTER_LINE_SYMBOL,
            chart_name="scatter_line_error_chart",
        )
        Calc.goto_cell(cell_name="A123", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A141"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A142"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title="Impact Energy (Joules)")
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))

        Lo.print("Adding y-axis error bars")
        sheet_name = Calc.get_sheet_name(sheet)
        error_label = f"{sheet_name}.C142"
        error_range = f"{sheet_name}.C143:C146"
        Chart2.set_y_error_bars(chart_doc=chart_doc, data_label=error_label, data_range=error_range)
        return chart_doc

    def _labeled_bubble_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a bubble chart with labels;
        # uses the "World data" table
        range_addr = Calc.get_address(sheet=sheet, range_name="H63:J93")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="A62",
            width=18,
            height=11,
            diagram_name=ChartTypes.Bubble.TEMPLATE_BUBBLE.BUBBLE,
            chart_name="labeled_bubble_chart",
        )
        Calc.goto_cell(cell_name="A62", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="H62"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="H63"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="I63"))
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)

        # change the data points
        ds = Chart2.get_data_series(chart_doc)
        Props.set(
            ds[0],
            Transparency=50,
            BorderStyle=LineStyle.SOLID,
            BorderColor=CommonColor.RED,
            LabelPlacement=DataPointLabelPlacementKind.CENTER.value,
        )

        # Chart2.set_data_point_labels(chart_doc=chart_doc, label_type=DataPointLabelTypeKind.NUMBER)

        sheet_name = Calc.get_sheet_name(sheet)
        label = f"{sheet_name}.K63"
        names = f"{sheet_name}.K64:K93"
        Chart2.add_cat_labels(chart_doc=chart_doc, data_label=label, data_range=names)
        return chart_doc

    def _net_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a net chart;
        # uses the "No of Calls per Day" table
        range_addr = Calc.get_address(sheet=sheet, range_name="A56:D63")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="E55",
            width=16,
            height=11,
            diagram_name=ChartTypes.Net.TEMPLATE_LINE.NET_LINE,
            chart_name="net_chart",
        )
        Calc.goto_cell(cell_name="E55", doc=doc)

        with Chart2ControllerLock(chart_doc=chart_doc):
            Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A55"))
            Chart2.view_legend(chart_doc=chart_doc, is_visible=True)
            Chart2.set_data_point_labels(chart_doc=chart_doc, label_type=DataPointLabelTypeKind.NONE)

            # reverse x-axis so days increase clockwise around net
            x_axis = Chart2.get_x_axis(chart_doc)
            sd = x_axis.getScaleData()
            sd.Orientation = AxisOrientation.REVERSE
            x_axis.setScaleData(sd)
        return chart_doc

    def _happy_stock_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a fancy stock chart
        # uses the "Happy Systems (HASY)" table

        range_addr = Calc.get_address(sheet=sheet, range_name="A86:F104")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="A105",
            width=25,
            height=14,
            diagram_name=ChartTypes.Stock.TEMPLATE_VOLUME.STOCK_VOLUME_OPEN_LOW_HIGH_CLOSE,
            chart_name="happy_stock_chart",
        )
        Calc.goto_cell(cell_name="A105", doc=doc)
        with Chart2ControllerLock(chart_doc=chart_doc):
            Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A85"))
            Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A86"))
            Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="B86"))
            Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
            Chart2.set_y_axis2_title(chart_doc=chart_doc, title="Stock Value")
            Chart2.rotate_y_axis2_title(chart_doc=chart_doc, angle=Angle(90))

            Chart2.set_data_point_labels(chart_doc=chart_doc, label_type=DataPointLabelTypeKind.NONE)
            # Chart2.view_legend(chart_doc=chart_doc, is_visible=True)

            # change 2nd y-axis min and max; default is poor ($0 - $20)
            y_axis2 = Chart2.get_y_axis2(chart_doc)
            sd = y_axis2.getScaleData()
            # Chart2.print_scale_data("Secondary Y-Axis", sd)
            sd.Minimum = 83
            sd.Maximum = 103
            y_axis2.setScaleData(sd)

            # change x-axis type from number to date
            x_axis = Chart2.get_x_axis(chart_doc)
            sd = x_axis.getScaleData()
            sd.AxisType = AxisType.DATE

            # set major increment to 3 days
            ti = TimeInterval(Number=3, TimeUnit=TimeUnit.DAY)
            tc = TimeIncrement()
            tc.MajorTimeInterval = ti
            sd.TimeIncrement = tc
            x_axis.setScaleData(sd)

            # rotate the axis labels by 45 degrees
            # x_axis = Chart2.get_x_axis(chart_doc)
            # Props.set(x_axis, TextRotation=45)

            # Chart2.print_chart_types(chart_doc)

            # change color of "WhiteDay" and "BlackDay" block colors
            ct = ChartTypes.Stock.NAMED.CANDLE_STICK_CHART
            candle_ct = Chart2.find_chart_type(chart_doc=chart_doc, chart_type=ct)
            # Props.show_obj_props("Stock chart", candle_ct)
            Chart2.color_stock_bars(ct=candle_ct, w_day_color=CommonColor.GREEN, b_day_color=CommonColor.RED)

            # thicken the high-low line; make it yellow
            ds = Chart2.get_data_series(chart_doc=chart_doc, chart_type=ct)
            Lo.print(f"No. of data series in candle stick chart: {len(ds)}")
            # Props.show_obj_props("Candle Stick", ds[0])
            Props.set(ds[0], LineWidth=120, Color=CommonColor.YELLOW)  # LineWidth in 1/100 mm
        return chart_doc

    def _stock_prices_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draws a stock chart, with an extra pork bellies line
        range_addr = Calc.get_address(sheet=sheet, range_name="E141:I146")
        chart_doc = Chart2.insert_chart(
            sheet=sheet,
            cells_range=range_addr,
            cell_name="E148",
            width=12,
            height=11,
            diagram_name=ChartTypes.Stock.TEMPLATE_VOLUME.STOCK_OPEN_LOW_HIGH_CLOSE,
            chart_name="stock_prices_chart",
        )
        Calc.goto_cell(cell_name="A139", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E140"))
        Chart2.set_data_point_labels(chart_doc=chart_doc, label_type=DataPointLabelTypeKind.NONE)
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="E141"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title="Dollars")
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))

        Lo.print("Adding Pork Bellies line")
        sheet_name = Calc.get_sheet_name(sheet)
        pork_label = f"{sheet_name}.J141"
        pork_points = f"{sheet_name}.J142:J146"
        Chart2.add_stock_line(chart_doc=chart_doc, data_label=pork_label, data_range=pork_points)

        Chart2.view_legend(chart_doc=chart_doc, is_visible=True)
        return chart_doc

    def _default_chart(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> XChartDocument:
        # draw a pie chart, with legend and subtitle;
        # uses "Top 5 States with the Most Elementary and Secondary Schools"

        # uses "Sneakers Sold this Month" table
        _ = Calc.set_selected_addr(doc=doc, sheet=sheet, range_name="A2:B8")
        chart_doc = Chart2.insert_chart(chart_name="defaut_chart")
        # Calc.goto_cell(cell_name="A1", doc=doc)

        Chart2.set_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A1"))
        Chart2.set_x_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="A2"))
        Chart2.set_y_axis_title(chart_doc=chart_doc, title=Calc.get_string(sheet=sheet, cell_name="B2"))
        # rotate x-axis which is now the vertical axis
        Chart2.rotate_y_axis_title(chart_doc=chart_doc, angle=Angle(90))
        return chart_doc

    def _default_dispatch(self, doc: XSpreadsheetDocument, sheet: XSpreadsheet) -> None:
        # draw a pie chart, with legend and subtitle;
        # uses "Top 5 States with the Most Elementary and Secondary Schools"

        # uses "Sneakers Sold this Month" table
        _ = Calc.set_selected_addr(doc=doc, sheet=sheet, range_name="A2:B8")
        Lo.dispatch_cmd(cmd="InsertObjectChart")
