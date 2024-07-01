from __future__ import annotations
from typing import cast, Dict, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.code.py_source_mgr import PyInstance


class DispatchPyObjState(XDispatch, EventsPartial, unohelper.Base):
    """If the View is not in PY_OBJ state the it is switched into PY_OBJ State."""

    def __init__(self, sheet: str, cell: str):
        XDispatch.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self.add_event_observers(SharedEvent().event_observer)
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
                return

            ctl_state = CtlState(cell=cell)
            state = ctl_state.get_state()
            if state == StateKind.UNKNOWN:
                self._log.error("Unknown State. Cannot proceed.")
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = False
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                return
            if state == StateKind.PY_OBJ:
                self._log.debug("Current State is PY_OBJ. Nothing to do.")
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = False
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                return

            ctl_state.set_state(value=StateKind.PY_OBJ)

            self._log.debug("Changing State to PY_OBJ")
            self._set_formula(cell=cell, dd_args=cargs.event_data)
            eargs = EventArgs.from_args(cargs)
            eargs.event_data.success = True
            self.trigger_event(f"{url.Main}_after_dispatch", eargs)
            return

        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self._log.error(f"Error: {e}", exc_info=True)
            return

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
