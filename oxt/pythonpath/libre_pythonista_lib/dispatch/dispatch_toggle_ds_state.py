from __future__ import annotations
from typing import Any, cast, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.utils.data_type.range_values import RangeValues
from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind
from ..code.py_source_mgr import PyInstance

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ooodev.utils.data_type.cell_obj import CellObj
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    import pandas as pd
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.code.py_source_mgr import PyInstance


class DispatchToggleDsState(unohelper.Base, XDispatch):
    def __init__(self, sheet: str, cell: str):
        super().__init__()
        self._sheet = sheet
        self._cell = cell
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug(f"init: sheet={sheet}, cell={cell}")

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        pass

    def dispatch(self, url: URL, args: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        try:
            self._logger.debug(f"dispatch(): url={url}")
            doc = CalcDoc.from_current_doc()
            sheet = doc.sheets[self._sheet]
            cell = sheet[self._cell]

            cc = CellCache(doc)  # singleton
            # cm = CellMgr(doc)  # singleton
            cell_obj = cell.cell_obj
            sheet_idx = sheet.sheet_index
            if not cc.has_cell(cell=cell_obj, sheet_idx=sheet_idx):
                self._logger.error(f"Cell {self._cell} is not in the cache.")
                return

            # changing the formula should trigger the recalculation.
            # Toggle the formula from a cell formula to a array formula and vice versa.
            formula = cell.component.getFormula()
            if not formula:
                self._logger.error(f"Cell {self._cell} has no formula.")
                return

            ctl_state = CtlState(cell=cell)
            state = ctl_state.get_state()
            if state == StateKind.PY_OBJ:
                self._logger.debug("Current State to DataFrame")
                state = StateKind.ARRAY
            else:
                self._logger.debug("Current State to Array")
                state = StateKind.PY_OBJ
            ctl_state.set_state(value=state)

            if state == StateKind.ARRAY:
                self._logger.debug("Changing State to Array")
                # change the formula to an array formula
                # The formula must be removed from the cell.
                # The number of rows and cols must be gotten from the data.
                # A range must be constructed from the number of rows and cols.
                # The formula must be set as an array formula on the range.

                self._set_array_formula(cell=cell)
                return

            if state == StateKind.PY_OBJ:
                self._logger.debug("Changing State to DataFrame")
                self._set_formula(cell=cell)
            return

        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self._logger.error(f"Error: {e}", exc_info=True)
            return

    def _set_array_formula(self, cell: CalcCell) -> None:
        cm = CellMgr(cell.calc_doc)  # singleton
        formula = self._get_formula(cell)
        if not formula:
            self._logger.error(f"Cell {cell.cell_obj} has no formula.")
            return
        self._logger.debug(f"_set_array_formula() Formula: {formula}")
        cell_obj = cell.cell_obj
        rows, cols = self._get_rows_cols(cell.calc_doc, cell_obj)
        ca = cell_obj.get_cell_address()
        rv = RangeValues(
            col_start=ca.Column,
            col_end=ca.Column + max(0, cols - 1),
            row_start=ca.Row,
            row_end=ca.Row + max(0, rows - 1),
        )
        ro = RangeObj.from_range(rv)
        cell_rng = cell.calc_sheet.get_range(range_obj=ro)

        with cm.listener_context(cell.component):
            cell.component.setFormula("")
            cell_rng.component.setArrayFormula(formula)
        cm.update_control(cell)

    def _set_formula(self, cell: CalcCell) -> None:
        formula = self._get_formula(cell)
        if not formula:
            self._logger.error(f"Cell {cell.cell_obj} has no formula.")
            return
        cm = CellMgr(cell.calc_doc)  # singleton
        sheet = cell.calc_sheet
        self._logger.debug(f"_set_formula() Formula: {formula}")
        cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
        cursor.collapseToCurrentArray()
        with cm.listener_context(cell.component):
            cursor.setArrayFormula("")
            cell.component.setFormula(formula)
        cm.update_control(cell)

    def _get_formula(self, cell: CalcCell) -> str:
        formula = cell.component.getFormula()
        if not formula:
            return ""
        formula = formula.lstrip("{").rstrip("}")
        return formula

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        pass

    def _set_formula_array(self, cell: CalcCell, formula: str) -> None:
        sheet = cell.calc_sheet
        cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
        cursor.collapseToCurrentArray()
        cursor.setArrayFormula(formula)

    def _get_data(self, doc: CalcDoc, cell_obj: CellObj) -> Any:
        py_inst = PyInstance(doc)  # singleton
        py_src = py_inst[cell_obj]
        return py_src.value

    def _get_rows_cols(self, doc: CalcDoc, cell: CellObj) -> Tuple[int, int]:
        s = cast("pd.Series", self._get_data(doc, cell))
        return len(s), 1
