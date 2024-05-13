from __future__ import annotations

import uno
from com.sun.star.drawing import XDrawPagesSupplier
from com.sun.star.drawing import XDrawPageSupplier
from com.sun.star.lang import XComponent
from com.sun.star.sheet import XSpreadsheet
from com.sun.star.sheet import XSpreadsheetDocument

from ooodev.format import Styler
from ooodev.format.calc.direct.cell import borders as direct_borders
from ooodev.format.calc.modify.cell import borders as modify_borders
from ooodev.format.calc.modify.cell.alignment import HoriAlignKind, VertAlignKind, TextAlign
from ooodev.format.calc.modify.cell.background import Color as BgColor
from ooodev.format.calc.modify.cell.font import FontEffects
from ooodev.office.calc import Calc
from ooodev.office.draw import Draw
from ooodev.units import UnitMM
from ooodev.utils.color import CommonColor
from ooodev.utils.file_io import FileIO
from ooodev.utils.lo import Lo
from ooodev.utils.table_helper import TableHelper
from ooodev.utils.type_var import PathOrStr

try:
    from ooodev.office.chart2 import Chart2
except ImportError:
    # bug in LibreOffice 7.4, Fixed in 7.5
    Chart2 = None


class BuildTable:
    HEADER_STYLE_NAME = "My HeaderStyle"
    DATA_STYLE_NAME = "My DataStyle"

    def __init__(self, im_fnm: PathOrStr, out_fnm: PathOrStr, **kwargs) -> None:
        if FileIO.is_exist_file(im_fnm, False):
            self._im_fnm = FileIO.get_absolute_path(im_fnm)
        else:
            self._im_fnm = None
        if out_fnm:
            out_file = FileIO.get_absolute_path(out_fnm)
            _ = FileIO.make_directory(out_file)
            self._out_fnm = out_file
        else:
            self._out_fnm = ""
        self._add_pic = bool(kwargs.get("add_pic", False))
        self._add_chart = bool(kwargs.get("add_chart", False))
        self._add_style = bool(kwargs.get("add_style", True))

    def main(self) -> None:
        doc = Calc.get_current_doc()
        sheet = Calc.get_active_sheet(doc)

        self._convert_addresses(sheet)

        # other possible build methods
        # self._build_cells(sheet)
        # self._build_rows(sheet)
        # self._build_cols(sheet)

        self._build_array(sheet)

        if self._add_pic:
            self._add_picture(sheet=sheet, doc=doc)

        # add a chart
        if self._add_chart and Chart2:
            # assumes _build_array() has filled the spreadsheet with data
            rng_addr = Calc.get_address(sheet=sheet, range_name="B2:M4")
            chart_cell = "B6" if self._add_pic else "D6"
            Chart2.insert_chart(
                sheet=sheet, cells_range=rng_addr, cell_name=chart_cell, width=21, height=11, diagram_name="Column"
            )

        if self._add_style:
            self._create_styles(doc)
            self._apply_styles(sheet)

        if self._out_fnm:
            Lo.save_doc(doc=doc, fnm=self._out_fnm)

    # region Private Methods

    def _build_cells(self, sheet: XSpreadsheet) -> None:
        # column -- row
        header_vals = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
        for i, val in enumerate(header_vals):
            Calc.set_val(value=val, sheet=sheet, col=i + 1, row=0)

        # name
        vals = (31.45, 20.9, 117.5, 23.4, 114.5, 115.3, 171.3, 89.5, 41.2, 71.3, 25.4, 38.5)
        # start at B2
        for i, val in enumerate(vals):
            cell_name = TableHelper.make_cell_name(row=2, col=i + 2)
            Calc.set_val(value=val, sheet=sheet, cell_name=cell_name)

    def _build_rows(self, sheet: XSpreadsheet) -> None:
        vals = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
        Calc.set_row(sheet=sheet, values=vals, cell_name="B1")
        Calc.set_val(value="SUM", sheet=sheet, cell_name="N1")

        Calc.set_val(value="Smith", sheet=sheet, cell_name="A2")
        vals = (42, 58.9, -66.5, 43.4, 44.5, 45.3, -67.3, 30.5, 23.2, -97.3, 22.4, 23.5)
        Calc.set_row(sheet=sheet, values=vals, cell_name="B2")
        Calc.set_val(value="=SUM(B2:M2)", sheet=sheet, cell_name="N2")

        Calc.set_val(value="Jones", sheet=sheet, col=0, row=2)
        vals = (21, 40.9, -57.5, -23.4, 34.5, 59.3, 27.3, -38.5, 43.2, 57.3, 25.4, 28.5)
        Calc.set_row(sheet=sheet, values=vals, col_start=1, row_start=2)
        Calc.set_val(value="=SUM(B3:M3)", sheet=sheet, col=13, row=2)

        Calc.set_val(value="Brown", sheet=sheet, col=0, row=3)
        vals = (31.45, -20.9, -117.5, 23.4, -114.5, 115.3, -171.3, 89.5, 41.2, 71.3, 25.4, 38.5)
        Calc.set_row(sheet=sheet, values=vals, col_start=1, row_start=3)
        Calc.set_val(value="=SUM(A4:L4)", sheet=sheet, col=13, row=3)

    def _build_cols(self, sheet: XSpreadsheet) -> None:
        vals = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
        Calc.set_col(sheet=sheet, values=vals, cell_name="A2")
        Calc.set_val(value="SUM", sheet=sheet, cell_name="A14")

        Calc.set_val(value="Smith", sheet=sheet, cell_name="B1")
        vals = (42, 58.9, -66.5, 43.4, 44.5, 45.3, -67.3, 30.5, 23.2, -97.3, 22.4, 23.5)
        Calc.set_col(sheet=sheet, values=vals, cell_name="B2")
        Calc.set_val(value="=SUM(B2:M2)", sheet=sheet, cell_name="B14")

        Calc.set_val(value="Jones", sheet=sheet, col=2, row=0)
        vals = (21, 40.9, -57.5, -23.4, 34.5, 59.3, 27.3, -38.5, 43.2, 57.3, 25.4, 28.5)
        Calc.set_col(sheet=sheet, values=vals, col_start=2, row_start=1)
        Calc.set_val(value="=SUM(B3:M3)", sheet=sheet, col=2, row=13)

        Calc.set_val(value="Brown", sheet=sheet, col=3, row=0)
        vals = (31.45, -20.9, -117.5, 23.4, -114.5, 115.3, -171.3, 89.5, 41.2, 71.3, 25.4, 38.5)
        Calc.set_col(sheet=sheet, values=vals, col_start=3, row_start=1)
        Calc.set_val(value="=SUM(A4:L4)", sheet=sheet, col=3, row=13)

    def _build_array(self, sheet: XSpreadsheet) -> None:
        vals = (
            ("", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"),
            ("Smith", 42, 58.9, -66.5, 43.4, 44.5, 45.3, -67.3, 30.5, 23.2, -97.3, 22.4, 23.5),
            ("Jones", 21, 40.9, -57.5, -23.4, 34.5, 59.3, 27.3, -38.5, 43.2, 57.3, 25.4, 28.5),
            ("Brown", 31.45, -20.9, -117.5, 23.4, -114.5, 115.3, -171.3, 89.5, 41.2, 71.3, 25.4, 38.5),
        )
        Calc.set_array(values=vals, sheet=sheet, name="A1:M4")  # or just A1

        Calc.set_val(sheet=sheet, cell_name="N1", value="SUM")
        Calc.set_val(sheet=sheet, cell_name="N2", value="=SUM(B2:M2)")
        Calc.set_val(sheet=sheet, cell_name="N3", value="=SUM(B3:M3)")
        Calc.set_val(sheet=sheet, cell_name="N4", value="=SUM(B4:M4)")

    def _convert_addresses(self, sheet: XSpreadsheet) -> None:
        # cell name <--> position
        pos = Calc.get_cell_position(cell_name="AA2")
        print(f"Positon of AA2: ({pos.X}, {pos.Y})")

        cell = Calc.get_cell(sheet=sheet, col=pos.X, row=pos.Y)
        Calc.print_cell_address(cell)

        print(f"AA2: {Calc.get_cell_str(col=pos.X, row=pos.Y)}")
        print()

        # cell range name <--> position
        rng = Calc.get_cell_range_positions("A1:D5")
        print(f"Range of A1:D5: ({rng[0].X}, {rng[0].Y}) -- ({rng[1].X}, {rng[1].Y})")

        cell_rng = Calc.get_cell_range(
            sheet=sheet, col_start=rng[0].X, row_start=rng[0].Y, col_end=rng[1].X, row_end=rng[1].Y
        )
        Calc.print_address(cell_rng)
        print(
            "A1:D5: " + Calc.get_range_str(col_start=rng[0].X, row_start=rng[0].Y, col_end=rng[1].X, row_end=rng[1].Y)
        )
        print()

    def _add_picture(self, sheet: XSpreadsheet, doc: XSpreadsheetDocument) -> None:
        # add a picture to the draw page for this sheet
        if self._im_fnm is None:
            raise FileNotFoundError("No Picture was found")
        dp_sup = Lo.qi(XDrawPageSupplier, sheet, True)
        page = dp_sup.getDrawPage()
        x = 230 if self._add_chart else 125
        Draw.draw_image(slide=page, fnm=self._im_fnm, x=x, y=32)

        # look at all the draw pages
        supplier = Lo.qi(XDrawPagesSupplier, doc, True)
        pages = supplier.getDrawPages()
        print(f"1. No. of draw pages: {pages.getCount()}")

        comp_doc = Lo.qi(XComponent, doc, True)
        print(f"2. No. of draw pages: {Draw.get_slides_count(comp_doc)}")

    def _create_styles(self, doc: XSpreadsheetDocument) -> None:
        try:
            # create a style using Calc
            header_style = Calc.create_cell_style(doc=doc, style_name=BuildTable.HEADER_STYLE_NAME)

            # create formats to apply to header_style
            header_bg_color_style = BgColor(color=CommonColor.ROYAL_BLUE, style_name=BuildTable.HEADER_STYLE_NAME)
            effects_style = FontEffects(color=CommonColor.WHITE, style_name=BuildTable.HEADER_STYLE_NAME)
            txt_align_style = TextAlign(
                hori_align=HoriAlignKind.CENTER,
                vert_align=VertAlignKind.MIDDLE,
                style_name=BuildTable.HEADER_STYLE_NAME,
            )
            # Apply formatting to header_style
            Styler.apply(header_style, header_bg_color_style, effects_style, txt_align_style)

            # create style
            data_style = Calc.create_cell_style(doc=doc, style_name=BuildTable.DATA_STYLE_NAME)

            # create formats to apply to data_style
            footer_bg_color_style = BgColor(color=CommonColor.LIGHT_BLUE, style_name=BuildTable.DATA_STYLE_NAME)
            bdr_style = modify_borders.Borders(padding=modify_borders.Padding(left=UnitMM(5)))

            # Apply formatting to data_style
            Styler.apply(data_style, footer_bg_color_style, bdr_style, txt_align_style)

        except Exception as e:
            print(e)

    def _apply_styles(self, sheet: XSpreadsheet) -> None:
        Calc.change_style(sheet=sheet, style_name=BuildTable.HEADER_STYLE_NAME, range_name="B1:N1")
        Calc.change_style(sheet=sheet, style_name=BuildTable.HEADER_STYLE_NAME, range_name="A2:A4")
        Calc.change_style(sheet=sheet, style_name=BuildTable.DATA_STYLE_NAME, range_name="B2:N4")

        # create a border side, default width units are points
        side = direct_borders.Side(width=2.85, color=CommonColor.DARK_BLUE)
        # create a border setting bottom side
        bdr = direct_borders.Borders(bottom=side)
        # Apply border to range
        Calc.set_style_range(sheet=sheet, range_name="A4:N4", styles=[bdr])

        # create a border with left and right
        bdr = direct_borders.Borders(left=side, right=side)
        # Apply border to range
        Calc.set_style_range(sheet=sheet, range_name="N1:N4", styles=[bdr])

    # endregion Private Methods

    # region properties
    @property
    def add_pic(self) -> bool:
        return self._add_pic

    @add_pic.setter
    def add_pic(self, value: bool):
        self._add_pic = value

    @property
    def add_chart(self) -> bool:
        return self._add_chart

    @add_chart.setter
    def add_chart(self, value: bool):
        self._add_chart = value

    @property
    def add_style(self) -> bool:
        return self._add_style

    @add_style.setter
    def add_style(self, value: bool):
        self._add_style = value

    # endregion properties
