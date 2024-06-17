from __future__ import annotations
from typing import Any, cast, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.calc import CalcDoc, CalcCell
from ooo.dyn.awt.message_box_type import MessageBoxType
from ooodev.dialog.msgbox import MsgBox
from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
from ..code.cell_cache import CellCache
from ..cell.props.key_maker import KeyMaker
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind
from ..res.res_resolver import ResResolver

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    import pandas as pd
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DispatchDelPyCell(unohelper.Base, XDispatch):
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
            formula = cell.component.getFormula()
            if not formula:
                self._logger.error(f"Cell {self._cell} has no formula.")
                return
            rr = ResResolver()
            msg_result = MsgBox.msgbox(
                msg=rr.resolve_string("mbmsg004"),
                title=rr.resolve_string("mbtitle004"),
                boxtype=MessageBoxType.QUERYBOX,
                buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
            )
            if msg_result != MessageBoxResultsEnum.YES:
                return
            key_maker = KeyMaker()  # singleton
            is_array_cell = cell.get_custom_property(key_maker.cell_array_ability_key, False)
            if is_array_cell:
                ctl_state = CtlState(cell=cell)
                state = ctl_state.get_state()
                if state == StateKind.PY_OBJ:
                    self._logger.debug("Current State to DataFrame")
                    self._remove_formula(cell=cell)
                else:
                    self._logger.debug("Current State to Array")
                    self._remove_formula_array(cell=cell)
                return
            self._remove_formula(cell=cell)

        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self._logger.error(f"Error: {e}", exc_info=True)
            return

    def _remove_formula(self, cell: CalcCell) -> None:
        formula = self._get_formula(cell)
        if not formula:
            self._logger.error(f"_remove_formula() Cell {cell.cell_obj} has no formula.")
            return
        self._logger.debug(f"_remove_formula() Formula: {formula}")
        cell.component.setFormula("")

    def _remove_formula_array(self, cell: CalcCell) -> None:
        formula = self._get_formula(cell)
        if not formula:
            self._logger.error(f"_remove_formula_array() Cell {cell.cell_obj} has no formula.")
            return
        sheet = cell.calc_sheet
        self._logger.debug(f"_remove_formula_array() Formula: {formula}")
        cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
        cursor.collapseToCurrentArray()
        cursor.setArrayFormula("")

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
