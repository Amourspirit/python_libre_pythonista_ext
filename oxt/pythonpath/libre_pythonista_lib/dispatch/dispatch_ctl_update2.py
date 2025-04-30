from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING

import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent
from ooodev.calc import CalcDoc

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_refresh_control import CmdRefreshControl
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_refresh_control import CmdRefreshControl
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class DispatchCtlUpdate2(XDispatch, LogMixin, unohelper.Base):
    """Refreshes the control in the cell."""

    def __init__(self, sheet: str, cell: str) -> None:
        XDispatch.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self.log.debug("init: sheet=%s, cell=%s", sheet, cell)
        self._status_listeners: Dict[str, XStatusListener] = {}
        self._command_handler = CmdHandlerFactory.get_cmd_handler()

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        self.log.debug("addStatusListener(): url=%s", URL.Main)
        if URL.Complete in self._status_listeners:
            self.log.debug("addStatusListener(): url=%s already exists.", URL.Main)
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

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        try:
            self.log.debug("dispatch(): url=%s", URL.Main)
            doc = CalcDoc.from_current_doc()
            sheet = doc.sheets[self._sheet]
            cell = sheet[self._cell]
            cmd = CmdRefreshControl(cell=cell, force_refresh=True)
            self._command_handler.handle(cmd)
            if cmd.success:
                self.log.debug("dispatch(): cmd success")
            else:
                self.log.debug("dispatch(): cmd failed")

        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self.log.error("Error: %s", e, exc_info=True)
            return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        Un-registers a listener from a control.
        """
        self.log.debug("removeStatusListener(): url=%s", URL.Main)
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]
