from __future__ import annotations
from typing import Any, cast, Dict, Tuple, List, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.utils.data_type.range_values import RangeValues
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind
from ..code.py_source_mgr import PyInstance
from ..event.shared_cell_event import SharedCellEvent
from ..sheet.range.rng_util import RangeUtil
from ..ex import CellFormulaExpandError

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ooodev.utils.data_type.cell_obj import CellObj
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    import pandas as pd
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.code.py_source_mgr import PyInstance


class DispatchToggleDataTblState(XDispatch, EventsPartial, unohelper.Base):
    def __init__(self, sheet: str, cell: str):
        XDispatch.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self.add_event_observers(SharedCellEvent().event_observer)
        self._log.debug(f"init: sheet={sheet}, cell={cell}")
        self._status_listeners: Dict[str, XStatusListener] = {}

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        self._log.debug(f"addStatusListener(): url={url.Main}")
        if url.Complete in self._status_listeners:
            self._log.debug(f"addStatusListener(): url={url.Main} already exists.")
        else:
            self._status_listeners[url.Complete] = control

    def dispatch(self, url: URL, args: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        try:
            self._log.debug(f"dispatch(): url={url.Main}")
            doc = CalcDoc.from_current_doc()
            sheet = doc.sheets[self._sheet]
            cell = sheet[self._cell]
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(
                url=url,
                args=args,
                doc=doc,
                sheet=sheet,
                cell=cell,
            )
            self.trigger_event(f"{url.Main}_before_dispatch", cargs)
            if cargs.cancel:
                self._log.debug(f"Event {url.Main}_before_dispatch was cancelled.")
                return
            cc = CellCache(doc)  # singleton
            # cm = CellMgr(doc)  # singleton
            cell_obj = cell.cell_obj
            sheet_idx = sheet.sheet_index
            if not cc.has_cell(cell=cell_obj, sheet_idx=sheet_idx):
                self._log.error(f"Cell {self._cell} is not in the cache.")
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = False
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                return

            # changing the formula should trigger the recalculation.
            # Toggle the formula from a cell formula to a array formula and vice versa.
            formula = cell.component.getFormula()
            if not formula:
                self._log.error(f"Cell {self._cell} has no formula.")
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = False
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                return

            ctl_state = CtlState(cell=cell)
            state = ctl_state.get_state()
            orig_state = state
            if state == StateKind.PY_OBJ:
                self._log.debug("Current State to DataFrame")
                state = StateKind.ARRAY
            else:
                self._log.debug("Current State to Array")
                state = StateKind.PY_OBJ
            ctl_state.set_state(value=state)

            if state == StateKind.ARRAY:
                self._log.debug("Changing State to Array")
                # change the formula to an array formula
                # The formula must be removed from the cell.
                # The number of rows and cols must be gotten from the data.
                # A range must be constructed from the number of rows and cols.
                # The formula must be set as an array formula on the range.

                try:
                    self._set_array_formula(cell=cell, dd_args=cargs.event_data)
                except Exception:
                    ctl_state.set_state(value=orig_state)
                    raise
            elif state == StateKind.PY_OBJ:

                try:
                    self._log.debug("Changing State to Data Table")
                    self._set_formula(cell=cell, dd_args=cargs.event_data)
                except Exception:
                    ctl_state.set_state(value=orig_state)
                    raise
            else:
                self._log.warning(f"Invalid State: {state}")
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = False
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                return

            eargs = EventArgs.from_args(cargs)
            eargs.event_data.success = True
            self.trigger_event(f"{url.Main}_after_dispatch", eargs)
            return

        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self._log.error(f"Error: {e}", exc_info=True)
            return

    def _set_array_formula(self, cell: CalcCell, dd_args: DotDict) -> None:
        cm = CellMgr(cell.calc_doc)  # singleton
        formula = self._get_formula(cell)
        if not formula:
            self._log.error(f"Cell {cell.cell_obj} has no formula.")
            return
        self._log.debug(f"_set_array_formula() Formula: {formula}")
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

        rng_util = RangeUtil(doc=cell.calc_doc)
        if not rng_util.get_cell_can_expand(cell_rng):
            msg = f"Range can not expand into range: {ro}"
            if cell.calc_sheet.is_sheet_protected():
                msg += " Sheet is protected. Cells may be protected or contain other data."
            else:
                msg += " Cells may contain other data."
            self._log.error(msg)
            raise CellFormulaExpandError(msg)

        dd = DotDict()
        for key, value in dd_args.items():
            dd[key] = value
        with cm.listener_context(cell.component):
            cell.component.setFormula("")
            eargs = EventArgs(self)
            eargs.event_data = dd
            self.trigger_event("dispatch_removed_cell_formula", eargs)

            cell_rng.component.setArrayFormula(formula)
            eargs.event_data.range_obj = ro
            self.trigger_event("dispatch_add_array_formula", eargs)

        cm.update_control(cell)

    def _set_formula(self, cell: CalcCell, dd_args: DotDict) -> None:
        formula = self._get_formula(cell)
        if not formula:
            self._log.error(f"Cell {cell.cell_obj} has no formula.")
            return
        cm = CellMgr(cell.calc_doc)  # singleton
        sheet = cell.calc_sheet
        self._log.debug(f"_set_formula() Formula: {formula}")
        cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
        cursor.collapseToCurrentArray()
        dd = DotDict()
        for key, value in dd_args.items():
            dd[key] = value
        with cm.listener_context(cell.component):
            eargs = EventArgs(self)
            rng_addr = cursor.getRangeAddress()

            dd.range_obj = RangeObj.from_range(rng_addr)
            eargs.event_data = dd
            self.trigger_event("dispatch_remove_array_formula", eargs)
            del eargs.event_data["range_obj"]
            cursor.setArrayFormula("")
            cell.component.setFormula(formula)
            self.trigger_event("dispatch_added_cell_formula", eargs)
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
        self._log.debug(f"removeStatusListener(): url={url.Main}")
        if url.Complete in self._status_listeners:
            del self._status_listeners[url.Complete]

    def _set_formula_array(self, cell: CalcCell, formula: str) -> None:
        sheet = cell.calc_sheet
        cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
        cursor.collapseToCurrentArray()
        cursor.setArrayFormula(formula)

    def _get_data(self, doc: CalcDoc, cell_obj: CellObj) -> DotDict:
        py_inst = PyInstance(doc)  # singleton
        py_src = py_inst[cell_obj]
        return py_src.dd_data

    def _get_rows_cols(self, doc: CalcDoc, cell: CellObj) -> List[int]:
        dd = self._get_data(doc, cell)

        lst_data = cast(List[List[Any]], dd.data)
        rows = len(lst_data)
        if rows == 0:
            return [0, 0]
        first = lst_data[0]
        cols = len(first)
        return [rows, cols]
