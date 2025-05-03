# region Imports
from __future__ import annotations
import uno
from typing import Any, cast, TYPE_CHECKING, List, Optional
from ooo.dyn.awt.push_button_type import PushButtonType
from ooo.dyn.awt.pos_size import PosSize

from ooodev.dialog import BorderKind
from ooodev.calc import CalcCell, RangeObj
from ooodev.loader import Lo


if TYPE_CHECKING:
    from oxt.___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from oxt.pythonpath.libre_pythonista_lib.utils.pandas_util import PandasUtil
    from oxt.pythonpath.libre_pythonista_lib.data.tbl_data_obj import TblDataObj
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from libre_pythonista_lib.utils.pandas_util import PandasUtil
    from libre_pythonista_lib.data.tbl_data_obj import TblDataObj
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.utils.result import Result


# endregion Imports


class TblDataCard2(LogMixin):
    # pylint: disable=unused-argument
    # region Init
    def __init__(self, cell: CalcCell) -> None:
        LogMixin.__init__(self)
        self._rr = ResourceResolver(Lo.get_context())
        self._border_kind = BorderKind.BORDER_SIMPLE
        self._width = 600
        self._height = 410
        self._btn_width = 100
        self._btn_height = 30
        self._margin = 6
        self._vert_margin = 12
        self._box_height = 30
        self._title = self._rr.resolve_string("dlgCardTblDataTitle")
        self._msg = self._rr.resolve_string("strDataTable")
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 10
        else:
            self._padding = 14
        self._row_index = -1
        self._cell = cell
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._module_state = cast(Optional[ModuleStateItem], None)
        self._doc = self._cell.calc_doc
        self._init_dialog()
        self._set_table_data()
        self.log.debug("init done for cell %s", self._cell.cell_obj)

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        self._dialog = self._doc.create_dialog(x=-1, y=-1, width=self._width, height=self._height, title=self._title)
        self._init_label()
        self._init_table()
        self._init_buttons()

    def _init_label(self) -> None:
        """Add a fixed text label to the dialog control"""
        self._ctl_main_lbl = self._dialog.insert_label(
            label=self._msg,
            x=self._margin,
            y=self._padding,
            width=self._width - (self._padding * 2),
            height=self._box_height,
        )

    def _init_table(self) -> None:
        """Add a Grid (table) to the dialog control"""
        sz = self._ctl_main_lbl.view.getPosSize()
        self._ctl_table1 = self._dialog.insert_table_control(
            x=sz.X,
            y=sz.Y + sz.Height + self._margin,
            width=sz.Width,
            height=300,
            grid_lines=True,
            col_header=True,
            row_header=True,
        )

    def _init_buttons(self) -> None:
        """Add OK, Cancel and Info buttons to dialog control"""
        self._ctl_btn_ok = self._dialog.insert_button(
            label=self._rr.resolve_string("dlg01"),
            x=self._width - self._btn_width - self._margin,
            y=self._height - self._btn_height - self._vert_margin,
            width=self._btn_width,
            height=self._btn_height,
            btn_type=PushButtonType.CANCEL,
        )

    # endregion Init

    # region Data
    def _get_message(self) -> str:
        """Get the message to display in the dialog."""
        data = cast(List[List[Any]], self.module_state.dd_data.data)
        rows, cols = self._get_rows_cols(data)

        df_str = self._rr.resolve_string("strDataTable")
        return f"{rows} x {cols} {df_str}"

    def _set_table_data(self) -> None:
        data = cast(List[List[Any]], self.module_state.dd_data.data)
        rows, cols = self._get_rows_cols(data)

        if rows <= 5:  # noqa: SIM108
            tbl = self._get_table_data_head()
        else:
            tbl = self._get_table_data_head_tail()

        self._ctl_table1.set_table_data(
            data=tbl,
            align="RLC",
            # widths=widths,
            has_row_headers=self._get_has_row_header(),
            has_colum_headers=False,
        )
        self._ctl_table1.horizontal_scrollbar = True

    def _get_has_row_header(self) -> bool:
        """Check if the range has headers. Considered to be a header if the first row is all string values."""
        try:
            if not "range_obj" in self.module_state.dd_data:
                return False
            ro = cast(RangeObj, self.module_state.dd_data.range_obj)
            cell_rng = self._cell.calc_sheet.get_range(range_obj=ro)
            tdo = TblDataObj(cell_rng)
            return tdo.has_headers
        except Exception:
            self.log.exception("Error getting range object")
            return False

    def _get_table_data_head(self) -> list:
        """Convert the dataframe and display in dialog grid control."""
        data = cast(List[List[Any]], self.module_state.dd_data.data)

        row_count = max(len(data), 5)

        # get the first five rows
        head_data = data[:row_count]
        PandasUtil.convert_array_to_lo(head_data)
        return head_data

    def _get_rows_cols(self, lst_data: List[List[Any]]) -> List[int]:
        rows = len(lst_data)
        if rows == 0:
            return [0, 0]
        first = lst_data[0]
        cols = len(first)
        return [rows, cols]

    def _get_table_data_head_tail(self) -> list:
        """Convert the dataframe and display in dialog grid control."""
        data = cast(List[List[Any]], self.module_state.dd_data.data)

        rows, cols = self._get_rows_cols(data)

        row_count = max(len(data), 10)

        if row_count < 2:
            self.log.error("_get_table_data_head_tail() Row count is less than 2: %i", row_count)
            raise ValueError("Row count is less than 2")

        end = row_count // 2
        start = row_count - end

        head_data = data[:start]
        tail_data = data[-end:]
        PandasUtil.convert_array_to_lo(head_data)
        PandasUtil.convert_array_to_lo(tail_data)

        # create a row of ellipse to insert before tail.
        ellipse = ["..." for _ in range(cols)]  # one extra column for row index
        tbl = head_data + [ellipse] + tail_data
        return tbl

    # endregion Data

    # region Show Dialog
    def show(self) -> int:
        with self.log.indent(True):
            # window = Lo.get_frame().getContainerWindow()
            self._doc.activate()
            try:
                self._ctl_main_lbl.label = self._get_message()
            except Exception as ex:
                self.log.error("Error setting message: %s", ex)
            window = self._doc.get_frame().getContainerWindow()
            ps = window.getPosSize()
            x = round(ps.Width / 2 - self._width / 2)
            y = round(ps.Height / 2 - self._height / 2)
            self._dialog.set_pos_size(x, y, self._width, self._height, PosSize.POSSIZE)
            self._dialog.set_visible(True)
            result = self._dialog.execute()
            self._dialog.dispose()
            return result

    # endregion Show Dialog

    # region Query

    def _qry_module_state(self) -> ModuleStateItem:
        qry = QryModuleState(cell=self._cell)
        result = self._qry_handler.handle(qry)
        if Result.is_failure(result):
            self.log.error("Error getting module state %s", result.error)
            raise result.error
        return result.data

    # endregion Query

    # region Properties

    @property
    def module_state(self) -> ModuleStateItem:
        if self._module_state is None:
            self._module_state = self._qry_module_state()
        return self._module_state

    # endregion Properties
