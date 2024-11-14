from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING
from threading import Thread

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.partial.events_partial import EventsPartial

from ..dialog.py.dialog_mb import DialogMb
from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..code.py_source_mgr import PyInstance
from ..event.shared_event import SharedEvent
from ..log.log_inst import LogInst
from ..cell.code_edit.cell_code_edit import CellCodeEdit

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
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
    with log.indent(True):
        log.debug(f"thread_wrapper inst_id: {inst_id}")
    try:
        original_func(inst_id, cell, url)
    finally:
        with log.indent(True):
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
    with log.indent(True):
        log.debug(f"dispatch_in_thread inst_id: {inst_id}")
    if inst_id in _ACTIVE_WINDOWS:
        with log.indent(True):
            log.debug(
                f"dispatch_in_thread inst_id: {inst_id} is in active windows. Deleting it."
            )
        del _ACTIVE_WINDOWS[inst_id]
    with log.indent(True):
        log.debug("dispatch_in_thread creating DispatchWorker")
    worker = DispatchCellCodeEdit(inst_id, cell, url.Main)
    with log.indent(True):
        log.debug("dispatch_in_thread dispatching DispatchWorker")
    worker.update_cell()
    with log.indent(True):
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

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self._log.indent(True):
            self._log.debug(f"addStatusListener(): url={URL.Main}")
            if URL.Complete in self._status_listeners:
                self._log.debug(f"addStatusListener(): url={URL.Main} already exists.")
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=URL, IsEnabled=True, State=None)
                Control.statusChanged(fe)
                self._status_listeners[URL.Complete] = Control

    @override
    def dispatch(self, URL: URL, Arguments: Tuple[PropertyValue, ...]) -> None:
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
                with self._log.indent(True):
                    self._log.debug(
                        f"Thread with inst_id '{self._inst_id}' is already running. Setting Focus"
                    )
                _ACTIVE_WINDOWS[self._inst_id].set_focus()
                return
            if self._inst_id not in _THREADS_DICT:
                # Wrap the original function
                target_func = lambda: thread_wrapper(
                    self._inst_id, cell, URL, dispatch_in_thread
                )
                t = Thread(target=target_func, daemon=True)

                # Add the thread to the dictionary
                _THREADS_DICT[self._inst_id] = t

                t.start()
                if self._in_thread:
                    with self._log.indent(True):
                        self._log.debug(
                            f"Thread with inst_id '{self._inst_id}' is running. Waiting for join."
                        )
                    t.join()
                    with self._log.indent(True):
                        self._log.debug(
                            f"Thread with inst_id '{self._inst_id}' has joined."
                        )
                else:
                    with self._log.indent(True):
                        self._log.debug(
                            f"Thread with inst_id '{self._inst_id}' is running. Did not wait for join."
                        )
            else:
                with self._log.indent(True):
                    self._log.debug(
                        f"Thread with inst_id '{self._inst_id}' is already running."
                    )

        except Exception:
            with self._log.indent(True):
                self._log.error("Error getting cell information", exc_info=True)
            return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        with self._log.indent(True):
            self._log.debug(f"removeStatusListener(): url={URL.Main}")
            if URL.Complete in self._status_listeners:
                del self._status_listeners[URL.Complete]


class DispatchCellCodeEdit(CellCodeEdit):
    def __init__(
        self, inst_id: str, cell: CalcCell, url_str: str = "", src_code: str = ""
    ):
        CellCodeEdit.__init__(self, inst_id, cell, url_str, src_code)

    @override
    def edit_code(self) -> bool:
        return edit_code(
            inst_id=self.inst_id,
            calc_cell=self.cell,
            log=self.log,
            src_code=self.src_code,
        )


def edit_code(
    inst_id: str, calc_cell: CalcCell, log: OxtLogger, src_code: str = ""
) -> bool:
    global _ACTIVE_WINDOWS
    cell_obj = calc_cell.cell_obj
    py_inst = PyInstance(calc_cell.calc_doc)  # singleton
    if src_code:
        py_inst.update_source(code=src_code, cell=cell_obj)
        py_inst.update_all()
        return True

    ctx = Lo.get_context()
    if DialogMb.has_instance(inst_id):
        mb = DialogMb.get_instance(inst_id)
        code = mb.text
    else:
        py_src = py_inst[cell_obj]
        code = py_src.source_code
        py_src = None
        mb = DialogMb(ctx=ctx, inst_id=inst_id, cell=calc_cell)
        mb.text = code
        mb.info = str(cell_obj)
    _ACTIVE_WINDOWS[inst_id] = mb

    log.debug("Displaying dialog")
    result = False
    if mb.show():
        with log.indent(True):
            log.debug("Dialog returned with OK")
        txt = mb.text.strip()
        if txt != code:
            try:
                with log.indent(True):
                    log.debug("Code has changed, updating ...")
                    py_inst.update_source(code=txt, cell=cell_obj)
                    log.debug(f"Cell Code updated for {cell_obj}")
                    py_inst.update_all()
                    log.debug("Code updated")
                result = True
            except Exception as e:
                with log.indent(True):
                    log.error("Error updating code", exc_info=True)
        else:
            with log.indent(True):
                log.debug("Code has not changed")
    else:
        with log.indent(True):
            log.debug("Dialog returned with Cancel")
    mb.dispose()
    return result
