from __future__ import annotations
from typing import Any, Dict, Tuple, TYPE_CHECKING

import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.loader import Lo

from ..py_pip.install_pip_pkg import InstallPipPkg

if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DispatchPyPkgUninstall(XDispatch, unohelper.Base):
    """Displays Dialog to uninstall a pip package."""

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XDispatch.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._status_listeners: Dict[str, XStatusListener] = {}

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        # https://wiki.openoffice.org/wiki/Documentation/DevGuide/WritingUNO/Implementation
        with self._log.indent(True):
            if URL.Complete in self._status_listeners:
                self._log.debug("addStatusListener(): url=%s already exists.", URL.Main)
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # setting State will affect how the control is displayed in menus.
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
            self._log.debug("dispatch(): url=%s", URL.Main)
            _ = Lo.current_doc
            installer = InstallPipPkg()
            installer.uninstall()

        except Exception as e:
            # log the error and do not re-raise it.
            # re-raising the error may crash the entire LibreOffice app.
            self._log.error(f"Error: {e}", exc_info=True)
            return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        Un-registers a listener from a control.
        """
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]
