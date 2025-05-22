from __future__ import annotations
from typing import Any, Dict, Tuple, TYPE_CHECKING, Callable
from threading import Thread

import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.partial.events_partial import EventsPartial


if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_refresh_control import CmdRefreshControl
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.dialog.py.dialog_mb import DialogMb
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_code_edit import CellCodeEdit
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code_exist import (
        QryCellSrcCodeExist,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr

else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode

    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_refresh_control import CmdRefreshControl
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code_exist import QryCellSrcCodeExist
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.dialog.py.dialog_mb import DialogMb
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_code_edit import CellCodeEdit
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr

    CmdHandlerT = Any
    QryHandlerT = Any

_THREADS_DICT = {}
_ACTIVE_WINDOWS = {}


def _get_qry_handler() -> QryHandlerT:
    return QryHandlerFactory.get_qry_handler()


def _get_cmd_handler() -> CmdHandlerT:
    return CmdHandlerFactory.get_cmd_handler()


def thread_wrapper(
    inst_id: str, cell: CalcCell, url: URL, original_func: Callable[[str, CalcCell, URL], None]
) -> None:
    """
    Wrapper function to execute the original thread function and remove the thread from the dictionary upon completion.
    """
    global _THREADS_DICT, _ACTIVE_WINDOWS
    log = LogInst()
    with log.indent(True):
        log.debug("thread_wrapper inst_id: %s", inst_id)
    try:
        original_func(inst_id, cell, url)
    finally:
        with log.indent(True):
            log.debug("thread_wrapper finally inst_id: %s", inst_id)
        # Remove the thread from the dictionary
        del _THREADS_DICT[inst_id]
        if inst_id in _ACTIVE_WINDOWS:
            del _ACTIVE_WINDOWS[inst_id]


def dispatch_in_thread(inst_id: str, cell: CalcCell, url: URL) -> None:
    """
    Handle the button action event.
    """
    global _ACTIVE_WINDOWS
    log = LogInst()
    with log.indent(True):
        log.debug("dispatch_in_thread inst_id: %s", inst_id)
    if inst_id in _ACTIVE_WINDOWS:
        with log.indent(True):
            log.debug("dispatch_in_thread inst_id: %s is in active windows. Deleting it.", inst_id)
        del _ACTIVE_WINDOWS[inst_id]
    with log.indent(True):
        log.debug("dispatch_in_thread creating DispatchWorker")
    worker = DispatchCellCodeEdit(inst_id, cell, url.Main)
    with log.indent(True):
        log.debug("dispatch_in_thread dispatching DispatchWorker")
    worker.update_cell()
    with log.indent(True):
        log.debug("dispatch_in_thread done")


class DispatchEditPyCellMb2(XDispatch, EventsPartial, unohelper.Base):
    def __init__(self, sheet: str, cell: str, in_thread: bool) -> None:
        XDispatch.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._in_thread = in_thread
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self.add_event_observers(SharedEvent().event_observer)
        self._log.debug("init: sheet=%s, cell=%s", sheet, cell)
        self._status_listeners: Dict[str, XStatusListener] = {}

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self._log.indent(True):
            self._log.debug("addStatusListener(): url=%s", URL.Main)
            if URL.Complete in self._status_listeners:
                self._log.debug("addStatusListener(): url=%s already exists.", URL.Main)
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=URL, IsEnabled=True, State=None)
                Control.statusChanged(fe)
                self._status_listeners[URL.Complete] = Control

    @override
    def dispatch(self, URL: URL, Arguments: Tuple[PropertyValue, ...]) -> None:  # noqa: N803
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
                    self._log.debug("Thread with inst_id '%s' is already running. Setting Focus", self._inst_id)
                _ACTIVE_WINDOWS[self._inst_id].set_focus()
                return
            if self._inst_id not in _THREADS_DICT:
                # Wrap the original function
                target_func = lambda: thread_wrapper(self._inst_id, cell, URL, dispatch_in_thread)
                t = Thread(target=target_func, daemon=True)

                # Add the thread to the dictionary
                _THREADS_DICT[self._inst_id] = t

                t.start()
                if self._in_thread:
                    with self._log.indent(True):
                        self._log.debug("Thread with inst_id '%s' is running. Waiting for join.", self._inst_id)
                    t.join()
                    with self._log.indent(True):
                        self._log.debug("Thread with inst_id '%s' has joined.", self._inst_id)
                else:
                    with self._log.indent(True):
                        self._log.debug("Thread with inst_id '%s' is running. Did not wait for join.", self._inst_id)
            else:
                with self._log.indent(True):
                    self._log.debug("Thread with inst_id '%s' is already running.", self._inst_id)

        except Exception:
            with self._log.indent(True):
                self._log.error("Error getting cell information", exc_info=True)
            return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        Un-registers a listener from a control.
        """
        with self._log.indent(True):
            self._log.debug("removeStatusListener(): url=%s", URL.Main)
            if URL.Complete in self._status_listeners:
                del self._status_listeners[URL.Complete]


class DispatchCellCodeEdit(CellCodeEdit):
    def __init__(self, inst_id: str, cell: CalcCell, url_str: str = "", src_code: str = "") -> None:
        CellCodeEdit.__init__(self, inst_id, cell, url_str, src_code)

    @override
    def edit_code(self) -> bool:
        return edit_code(
            inst_id=self.inst_id,
            calc_cell=self.cell,
            log=self.log,
            src_code=self.src_code,
        )


def edit_code(inst_id: str, calc_cell: CalcCell, log: OxtLogger, src_code: str = "") -> bool:
    global _ACTIVE_WINDOWS
    cell_obj = calc_cell.cell_obj
    log.debug("edit_code() cell: %s", cell_obj)

    qry_handler = _get_qry_handler()
    cmd_handler = _get_cmd_handler()
    qry_src_mgr = QryPySrcMgr(doc=calc_cell.calc_doc)
    py_src_mgr = qry_handler.handle(qry_src_mgr)
    has_source = cell_obj in py_src_mgr

    if src_code:
        qry_uri = QryCellUri(cell=calc_cell)
        uri_result = qry_handler.handle(qry_uri)
        if Result.is_failure(uri_result):
            log.error("Failed to get URI for cell %s", cell_obj)
            return False
        uri = uri_result.data

        qry_src_exist = QryCellSrcCodeExist(uri=uri, cell=calc_cell)
        src_exist = qry_handler.handle(qry_src_exist)
        success = True
        if src_exist:
            cmd = CmdUpdateCode(cell=calc_cell, mod=py_src_mgr.mod, code=src_code)
            cmd_handler.handle(cmd)
            if not cmd.success:
                log.error("Failed to update code")
            success = success and cmd.success
        else:
            cmd = CmdAppendCode(cell=calc_cell, mod=py_src_mgr.mod, code=src_code)
            cmd_handler.handle(cmd)
            if not cmd.success:
                log.error("Failed to append code")
            success = success and cmd.success
        if success:
            cmd = CmdRefreshControl(cell=calc_cell, mod=py_src_mgr.mod)
            cmd_handler.handle(cmd)
            if not cmd.success:
                log.error("Failed to refresh control")
            success = success and cmd.success
        return success

    ctx = Lo.get_context()
    if DialogMb.has_instance(inst_id):
        mb = DialogMb.get_instance(inst_id)
        code = mb.text
    else:
        py_inst = py_src_mgr[cell_obj]
        code = py_inst.source_code

        mb = DialogMb(ctx=ctx, inst_id=inst_id, cell=calc_cell)
        mb.text = code
        mb.info = str(cell_obj)

    _ACTIVE_WINDOWS[inst_id] = mb

    log.debug("Displaying dialog")
    success = True
    if mb.show():
        log.debug("Dialog returned with OK")
        txt = mb.text.strip()
        if txt != code:
            try:
                log.debug("Code has changed, updating ...")
                if has_source:
                    py_src_mgr.update_source(code=txt, cell_obj=calc_cell.cell_obj)
                    log.debug("Cell Code updated for %s", cell_obj)
                else:
                    py_src_mgr.add_source(code=txt, cell_obj=calc_cell.cell_obj)
                    log.debug("Cell Code added for %s", cell_obj)
                log.debug("Code updated")
                cmd = CmdRefreshControl(cell=calc_cell, mod=py_src_mgr.mod)
                cmd_handler.handle(cmd)
                if cmd.success:
                    log.debug("Control refreshed")
                else:
                    log.error("Failed to refresh control")
                success = success and cmd.success
            except Exception:
                log.error("Error updating code", exc_info=True)
                success = False
        else:
            log.debug("Code has not changed")
    else:
        with log.indent(True):
            log.debug("Dialog returned with Cancel")
        success = False
    mb.dispose()
    return success
