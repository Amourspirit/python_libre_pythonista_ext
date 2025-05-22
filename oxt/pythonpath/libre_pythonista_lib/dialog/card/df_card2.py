# region Imports
from __future__ import annotations
from typing import cast, TYPE_CHECKING, Tuple, Optional
from ooo.dyn.awt.push_button_type import PushButtonType
from ooo.dyn.awt.pos_size import PosSize

from ooodev.dialog import BorderKind
from ooodev.calc import CalcCell
from ooodev.units import UnitAppFontWidth
from ooodev.loader import Lo
import pandas as pd

if TYPE_CHECKING:
    from oxt.___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from oxt.pythonpath.libre_pythonista_lib.utils.pandas_util import PandasUtil
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from libre_pythonista_lib.utils.pandas_util import PandasUtil
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.utils.result import Result


# endregion Imports


class DfCard2(LogMixin):
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
        self._title = self._rr.resolve_string("dlgCardDfTitle")
        self._msg = self._rr.resolve_string("strDataFrame")
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
        state = self.module_state

        df = cast(pd.DataFrame, state.dd_data.data)
        msg_str = self._rr.resolve_string("strDataFrame")
        if not PandasUtil.is_dataframe(df):
            self.log.error("Data is not a DataFrame")
            return ""

        shape = df.shape
        shape_len = len(shape)
        if shape_len == 0:
            return msg_str
        if shape_len == 1:
            rows = shape[0]
            return f"{rows} x 0 {msg_str}"
        return f"{shape[0]} x {shape[1]} {msg_str}"

    def _set_table_data(self) -> None:
        state = self.module_state
        df = cast(pd.DataFrame, state.dd_data.data)

        if not PandasUtil.is_dataframe(df):
            self.log.error("Data is not a DataFrame")
            return
        rows = df.shape[0]
        if PandasUtil.is_describe_output(df):
            self.log.debug("DataFrame is a describe output")
            tbl, max_len = self._get_table_data_describe()
        else:
            if rows <= 5:
                tbl, max_len = self._get_table_data_head()
            else:
                tbl, max_len = self._get_table_data_head_tail()

        row_header_width = int(UnitAppFontWidth(max_len * 6))
        self.log.debug(f"_set_table_data() Row header width: {row_header_width}")
        self._ctl_table1.set_table_data(
            data=tbl,
            align="RLC",
            # widths=widths,
            has_row_headers=True,
            has_colum_headers=PandasUtil.has_headers(df),
            row_header_width=row_header_width,
        )
        self._ctl_table1.horizontal_scrollbar = True

    def _get_table_data_describe(self) -> Tuple[list, int]:
        """Convert the dataframe and display in dialog grid control."""
        state = self.module_state
        df = cast(pd.DataFrame, state.dd_data.data)

        tbl = PandasUtil.pandas_to_array(df)
        max_len = PandasUtil.get_df_index_max_len(df.describe())
        self.log.debug(f"_set_table_data() Max length: {max_len}")
        PandasUtil.convert_array_to_lo(tbl)
        return tbl, max_len

    def _get_table_data_head(self) -> Tuple[list, int]:
        """Convert the dataframe and display in dialog grid control."""
        state = self.module_state
        df = cast(pd.DataFrame, state.dd_data.data)

        head_data = df.head()
        max_len = PandasUtil.get_df_index_max_len(head_data)
        self.log.debug(f"_set_table_data() Max length: {max_len}")
        tbl = PandasUtil.pandas_to_array(df.head(), index_opt=1)
        PandasUtil.convert_array_to_lo(tbl)
        return tbl, max_len

    def _get_table_data_head_tail(self) -> Tuple[list, int]:
        """Convert the dataframe and display in dialog grid control."""
        state = self.module_state
        df = cast(pd.DataFrame, state.dd_data.data)

        _, cols = PandasUtil.get_df_rows_columns(df)
        head_data = df.head()
        tail_data = df.tail()
        head_max = PandasUtil.get_df_index_max_len(head_data)
        tail_max = PandasUtil.get_df_index_max_len(tail_data)
        max_len = max(head_max, tail_max)
        self.log.debug("_set_table_data() Max length: %i", max_len)
        head = PandasUtil.pandas_to_array(df.head(), index_opt=1, convert=False)
        tail = PandasUtil.pandas_to_array(df.tail(), header_opt=2, index_opt=1, convert=False)

        PandasUtil.convert_array_to_lo(head)
        PandasUtil.convert_array_to_lo(tail)
        # create a row of ellipse to insert before tail.
        ellipse = ["..." for _ in range(cols + 1)]  # one extra column for row index
        tbl = head + [ellipse] + tail
        return tbl, max_len

    # endregion Data

    # region Show Dialog
    def show(self) -> int:
        # window = Lo.get_frame().getContainerWindow()
        self._doc.activate()
        try:
            self._ctl_main_lbl.label = self._get_message()
        except Exception as ex:
            self.log.error(f"Error setting message: {ex}")
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
