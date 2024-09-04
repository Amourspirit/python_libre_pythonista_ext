from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING
from threading import Thread

import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.loader import Lo
from ooodev.events.partial.events_partial import EventsPartial

from ..dialog.log.dialog_log import DialogLog
from ..event.shared_event import SharedEvent
from ..log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

_THREADS_DICT = {}
_ACTIVE_WINDOWS = {}


def thread_wrapper(uid: str, url: URL, original_func):
    """
    Wrapper function to execute the original thread function and remove the thread from the dictionary upon completion.
    """
    global _THREADS_DICT, _ACTIVE_WINDOWS
    log = LogInst()
    with log.indent(True):
        log.debug(f"thread_wrapper uid: {uid}")
    try:
        original_func(uid, url)
    finally:
        with log.indent(True):
            log.debug(f"thread_wrapper finally uid: {uid}")
        # Remove the thread from the dictionary
        del _THREADS_DICT[uid]
        if uid in _ACTIVE_WINDOWS:
            del _ACTIVE_WINDOWS[uid]


def dispatch_in_thread(uid: str, url: URL):
    """
    Handle the button action event.
    """
    global _ACTIVE_WINDOWS
    log = LogInst()
    with log.indent(True):
        log.debug(f"dispatch_in_thread uid: {uid}")
    if uid in _ACTIVE_WINDOWS:
        with log.indent(True):
            log.debug(f"dispatch_in_thread uid: {uid} is in active windows. Deleting it.")
        del _ACTIVE_WINDOWS[uid]
    with log.indent(True):
        log.debug("dispatch_in_thread creating DispatchWorker")
    worker = DispatchWorker(uid, url)
    with log.indent(True):
        log.debug("dispatch_in_thread dispatching DispatchWorker")
    worker.dispatch()
    with log.indent(True):
        log.debug("dispatch_in_thread done")


class DispatchLogWindow(XDispatch, EventsPartial, unohelper.Base):
    def __init__(self, in_thread: bool):
        XDispatch.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init")
        self._log.debug(f"in_thread: {in_thread}")
        self._in_thread = in_thread
        self.add_event_observers(SharedEvent().event_observer)
        self._log.debug(f"init")
        self._status_listeners: Dict[str, XStatusListener] = {}

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self._log.indent(True):
            self._log.debug(f"addStatusListener(): url={url.Main}")
            if url.Complete in self._status_listeners:
                self._log.debug(f"addStatusListener(): url={url.Main} already exists.")
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=url, IsEnabled=True, State=None)
                control.statusChanged(fe)
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
            doc = Lo.current_doc
            self._uid = doc.runtime_uid
            if DialogLog.has_instance(self._uid):
                with self._log.indent(True):
                    self._log.debug(f"DialogLog has instance with uid '{self._uid}'. Setting Visible")
                inst = DialogLog.get_instance(self._uid)
                inst.show()
                return

            if self._uid in _ACTIVE_WINDOWS:
                with self._log.indent(True):
                    self._log.debug(f"Thread with uid '{self._uid}' is already running. Setting Focus")
                _ACTIVE_WINDOWS[self._uid].set_focus()
                return
            if self._uid not in _THREADS_DICT:
                # Wrap the original function
                target_func = lambda: thread_wrapper(self._uid, url, dispatch_in_thread)
                t = Thread(target=target_func, daemon=True)

                # Add the thread to the dictionary
                _THREADS_DICT[self._uid] = t

                t.start()
                if self._in_thread:
                    with self._log.indent(True):
                        self._log.debug(f"Thread with uid '{self._uid}' is running. Waiting for join.")
                    t.join()
                    with self._log.indent(True):
                        self._log.debug(f"Thread with uid '{self._uid}' has joined.")
                else:
                    with self._log.indent(True):
                        self._log.debug(f"Thread with uid '{self._uid}' is running. Did not wait for join.")
            else:
                with self._log.indent(True):
                    self._log.debug(f"Thread with uid '{self._uid}' is already running.")

        except Exception:
            with self._log.indent(True):
                self._log.error("Error getting cell information", exc_info=True)
            return

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        with self._log.indent(True):
            self._log.debug(f"removeStatusListener(): url={url.Main}")
            if url.Complete in self._status_listeners:
                del self._status_listeners[url.Complete]


class DispatchWorker:
    def __init__(self, uid: str, url: URL):
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug(f"init: uid={uid}, url={url.Main}")
        self._url = url
        self._uid = uid

    def dispatch(self) -> None:
        with self._log.indent(True):
            try:
                self._log.debug("dispatch")
                self._show_dialog()
            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error(f"Error: {e}", exc_info=True)
                return

    def _show_dialog(self) -> None:
        global _ACTIVE_WINDOWS
        ctx = Lo.get_context()
        if DialogLog.has_instance(self._uid):
            mb = DialogLog.get_instance(self._uid)
        else:
            mb = DialogLog(ctx)
        _ACTIVE_WINDOWS[self._uid] = mb
        with self._log.indent(True):
            self._log.debug("Displaying dialog")
        mb.show()
        return
        if mb.show():
            with self._log.indent(True):
                self._log.debug("Log Dialog is Closed.")
        mb.dispose()
