from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING

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

from ooodev.calc import CalcDoc
from ooodev.loader import Lo
from ..utils import str_util

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class DispatchRngSelectPopup(XDispatch, unohelper.Base):
    """If the View is not in PY_OBJ state the it is switched into PY_OBJ State."""

    def __init__(self, **kwargs):
        """
        Constructor:

        Keyword Args:
            close_on_mouse_release (bool, str): If True, the dialog will close on mouse release.
            single_cell_mode (bool, str): If True, the dialog will be in single cell mode.
            initial_value (str): The initial value for the dialog.
        """
        XDispatch.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._status_listeners: Dict[str, XStatusListener] = {}
        try:
            self._close_on_mouse_release = str_util.convert_to_bool(kwargs.get("close_on_mouse_release", False))
            self._single_cell_mode = str_util.convert_to_bool(kwargs.get("single_cell_mode", False))
            self._initial_value = str(kwargs.get("initial_value", ""))
        except Exception:
            self._close_on_mouse_release = False
            self._single_cell_mode = False
            self._initial_value = ""
            self._log.error("Error in constructor.", exc_info=True)
        try:
            self.ctx = Lo.get_context()
            self._rr = ResourceResolver(self.ctx)
        except Exception:
            self._log.error("Error in constructor.", exc_info=True)
            raise

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self._log.indent(True):
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

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        with self._log.indent(True):
            try:
                self._log.debug(f"dispatch(): url={URL.Main}")
                doc = CalcDoc.from_current_doc()
                # no need to run in a thread as it already runs in a thread.
                title = self._rr.resolve_string("strRngSelTitle")
                doc.invoke_range_selection(
                    title=title,
                    close_on_mouse_release=self._close_on_mouse_release,
                    single_cell_mode=self._single_cell_mode,
                    initial_value=self._initial_value,
                )
                return

            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error(f"Error: {e}", exc_info=True)
                return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]
