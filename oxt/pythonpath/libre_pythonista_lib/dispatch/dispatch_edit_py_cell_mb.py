from __future__ import annotations
from typing import cast, Dict, Tuple, TYPE_CHECKING
from threading import Thread

import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..dialog.py.dialog_mb import DialogMb
from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..code.py_source_mgr import PyInstance
from ..event.shared_event import SharedEvent
from ..log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ooodev.utils.data_type.cell_obj import CellObj
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

_THREADS_DICT = {}
_ACTIVE_WINDOWS = {}


def thread_wrapper(inst_id: str, cell: CalcCell, url: URL, original_func):
    """
    Wrapper function to execute the original thread function and remove the thread from the dictionary upon completion.
    """
    global _THREADS_DICT, _ACTIVE_WINDOWS
    log = LogInst()
    log.debug(f"thread_wrapper inst_id: {inst_id}")
    try:
        original_func(inst_id, cell, url)
    finally:
        log.debug(f"thread_wrapper finally inst_id: {inst_id}")
        # Remove the thread from the dictionary
        del _THREADS_DICT[inst_id]
        if inst_id in _ACTIVE_WINDOWS:
            del _ACTIVE_WINDOWS[inst_id]


def dispatch_in_thread(inst_id: str, cell: CalcCell, url: URL):
    """
    Handle the button action event.
    """
    global _ACTIVE_WINDOWS
    log = LogInst()
    log.debug(f"dispatch_in_thread inst_id: {inst_id}")
    if inst_id in _ACTIVE_WINDOWS:
        log.debug(f"dispatch_in_thread inst_id: {inst_id} is in active windows. Deleting it.")
        del _ACTIVE_WINDOWS[inst_id]
    log.debug("dispatch_in_thread creating DispatchWorker")
    worker = DispatchWorker(inst_id, cell, url)
    log.debug("dispatch_in_thread dispatching DispatchWorker")
    worker.dispatch()
    log.debug("dispatch_in_thread done")


class DispatchEditPyCellMb(XDispatch, EventsPartial, unohelper.Base):
    def __init__(self, sheet: str, cell: str, in_thread: bool):
        XDispatch.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._in_thread = in_thread
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self.add_event_observers(SharedEvent().event_observer)
        self._log.debug(f"init: sheet={sheet}, cell={cell}")
        self._status_listeners: Dict[str, XStatusListener] = {}

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

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
        """
        # this dispatch runs a the top window in a thread. This is necessary because
        # the top window mimics a dialog and runs a timer on a thread to wait for show()
        # method to be finished.
        # Also, this must be run in a separate dispatch, eg: menu.execute_cmd(command, in_thread=True), but only when run from popup menu
        # such as a popup menu created fro the Python button controls.
        # It does not seem to be possible to run a dispatch command in a thread from an intercepted menu command such as a right click on calc.
        # For some reason if the thread on not joined when this dispatch is launched from a popup menu, the GUI will lock up every so often.
        # I did not get the GUI to lock up when launching from an intercepted menu, only popup menu.
        # Below t.join() is called if the dispatch is called with the '&in_thread=1', which it is for popup menus.
        # If popup menu dispatch is not called in a thread it will block the GUI.
        # The dispatch can run without t.join(); However, the dispatch was failing and Locking the entire GUI from time to time
        # causing critical failure.
        # My testing outside dispatch did not show any issues. However, the dispatch is a different beast.
        # When this command was dispatched three times in a row on a Popup menu for the same cell control, the GUI locked up most every time.
        # Running t.join() seems to get rid of all the issues in this area.
        global _THREADS_DICT, _ACTIVE_WINDOWS
        try:
            doc = CalcDoc.from_current_doc()
            sheet = doc.sheets[self._sheet]
            cell = sheet[self._cell]
            self._inst_id = f"{doc.runtime_uid}_{sheet.sheet_index}_{cell.cell_obj}"

            if self._inst_id in _ACTIVE_WINDOWS:
                self._log.debug(f"Thread with inst_id '{self._inst_id}' is already running. Setting Focus")
                _ACTIVE_WINDOWS[self._inst_id].set_focus()
                return
            if self._inst_id not in _THREADS_DICT:
                # Wrap the original function
                target_func = lambda: thread_wrapper(self._inst_id, cell, url, dispatch_in_thread)
                t = Thread(target=target_func, daemon=True)

                # Add the thread to the dictionary
                _THREADS_DICT[self._inst_id] = t

                t.start()
                if self._in_thread:
                    self._log.debug(f"Thread with inst_id '{self._inst_id}' is running. Waiting for join.")
                    t.join()
                    self._log.debug(f"Thread with inst_id '{self._inst_id}' has joined.")
                else:
                    self._log.debug(f"Thread with inst_id '{self._inst_id}' is running. Did not wait for join.")
            else:
                self._log.debug(f"Thread with inst_id '{self._inst_id}' is already running.")

        except Exception:
            self._log.error("Error getting cell information", exc_info=True)
            return

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        self._log.debug(f"removeStatusListener(): url={url.Main}")
        if url.Complete in self._status_listeners:
            del self._status_listeners[url.Complete]


class DispatchWorker(EventsPartial):
    def __init__(self, inst_id: str, cell: CalcCell, url: URL):
        EventsPartial.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug(f"init: inst_id={inst_id}, cell={cell}, url={url.Main}")
        self._cell = cell
        self._url = url
        self._inst_id = inst_id

    def dispatch(self) -> None:
        try:
            self._log.debug(f"dispatch: cell={self._cell.cell_obj}")
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(
                cell=self._cell,
            )
            self.trigger_event(f"{self._url.Main}_before_dispatch", cargs)
            if cargs.cancel:
                self._log.debug(f"Event {self._url.Main}_before_dispatch was cancelled.")
                return

            cc = CellCache(self._cell.calc_doc)  # singleton
            cell_obj = self._cell.cell_obj
            sheet_idx = self._cell.calc_sheet.sheet_index
            if not cc.has_cell(cell=cell_obj, sheet_idx=sheet_idx):
                self._log.error(f"Cell {self._cell} is not in the cache.")
                return
            with cc.set_context(cell=cell_obj, sheet_idx=sheet_idx):
                result = self._edit_code(doc=self._cell.calc_doc, cell_obj=cell_obj)
                if result:
                    if self._cell.calc_doc.component.isAutomaticCalculationEnabled():
                        # the purpose of writing the formulas back to the cell(s) is to trigger the recalculation
                        cm = CellMgr(self._cell.calc_doc)  # singleton. Tracks all Code cells
                        # https://ask.libreoffice.org/t/mark-a-calc-sheet-cell-as-dirty/106659
                        with cm.listener_context(self._cell.component):
                            # suspend the listeners for this cell
                            formula = self._cell.component.getFormula()
                            if not formula:
                                self._log.error(f"Cell {self._cell} has no formula.")
                                eargs = EventArgs.from_args(cargs)
                                eargs.event_data.success = False
                                self.trigger_event(f"{self._url.Main}_after_dispatch", eargs)
                                return
                            # s = s.lstrip("=")  # just in case there are multiple equal signs
                            is_formula_array = False
                            if formula.startswith("{"):
                                is_formula_array = True
                                formula = formula.lstrip("{")
                                formula = formula.rstrip("}")

                            dd = DotDict()
                            for key, value in cargs.event_data.items():
                                dd[key] = value
                            eargs = EventArgs(self)
                            if is_formula_array:
                                # The try block is important. If there is a error without the block then the entire LibreOffice app can crash.
                                self._log.debug("Resetting array formula")
                                # get the cell that are involved in the array formula.
                                cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
                                # this next line also works.
                                # cursor = cast("SheetCellCursor", cell.component.getSpreadsheet().createCursorByRange(cell.component))  # type: ignore
                                cursor.collapseToCurrentArray()
                                # reset the array formula
                                cursor.setArrayFormula(formula)
                                rng_addr = cursor.getRangeAddress()
                                dd.range_obj = RangeObj.from_range(rng_addr)
                                eargs.event_data = dd
                                self.trigger_event("dispatch_remove_array_formula", eargs)
                            else:
                                self._log.debug("Resetting formula")
                                self._cell.component.setFormula(formula)
                                self.trigger_event("dispatch_added_cell_formula", eargs)
                            self._cell.calc_doc.component.calculate()
            eargs = EventArgs.from_args(cargs)
            eargs.event_data.success = True
            self.trigger_event(f"{self._url.Main}_after_dispatch", eargs)
        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self._log.error(f"Error: {e}", exc_info=True)
            return

    def _edit_code(self, doc: CalcDoc, cell_obj: CellObj) -> bool:
        global _ACTIVE_WINDOWS
        ctx = Lo.get_context()
        py_inst = PyInstance(doc)  # singleton
        if DialogMb.has_instance(self._inst_id):
            mb = DialogMb.get_instance(self._inst_id)
        else:
            py_src = py_inst[cell_obj]
            code = py_src.source_code
            py_src = None
            mb = DialogMb(ctx, self._inst_id)
            mb.text = code
            mb.info = str(self._cell.cell_obj)
        _ACTIVE_WINDOWS[self._inst_id] = mb

        self._log.debug("Displaying dialog")
        result = False
        if mb.show():
            self._log.debug("Dialog returned with OK")
            txt = mb.text.strip()
            if txt != code:
                try:
                    self._log.debug("Code has changed, updating ...")
                    py_inst.update_source(code=txt, cell=cell_obj)
                    self._log.debug(f"Cell Code updated for {cell_obj}")
                    py_inst.update_all()
                    self._log.debug("Code updated")
                    result = True
                except Exception as e:
                    self._log.error("Error updating code", exc_info=True)
            else:
                self._log.debug("Code has not changed")
        else:
            self._log.debug("Dialog returned with Cancel")
        mb.dispose()
        return result
