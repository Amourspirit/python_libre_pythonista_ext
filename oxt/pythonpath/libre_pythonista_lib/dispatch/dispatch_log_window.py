from __future__ import annotations
from typing import Any, Dict, Tuple, TYPE_CHECKING


import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override
    from com.sun.star.frame import XStatusListener
else:

    def override(func):  # noqa: ANN001, ANN201
        return func


class DispatchLogWindow(XDispatch, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.dispatch.DispatchLogWindow"
    SERVICE_NAMES = ("com.sun.star.frame.XDispatch",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any, in_thread: bool) -> None:  # noqa: ANN401
        XDispatch.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self._in_thread = in_thread
        self._status_listeners: Dict[str, XStatusListener] = {}

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        if URL.Complete in self._status_listeners:
            pass
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
        if TYPE_CHECKING:
            from .action.action_log_window import ActionLogWindow
        else:
            from libre_pythonista_lib.dispatch.action.action_log_window import ActionLogWindow

        action = ActionLogWindow(self._in_thread)
        action.dispatch(URL, Arguments)

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        Un-registers a listener from a control.
        """
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]


# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*DispatchLogWindow.get_imple())

# endregion Implementation
