from __future__ import annotations
from typing import Any, cast, Dict, Tuple, TYPE_CHECKING

import unohelper
from com.sun.star.uno import XInterface
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL

from ooo.dyn.beans.named_value import NamedValue
from ooo.dyn.frame.feature_state_event import FeatureStateEvent
from ooodev.loader import Lo

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.utils.custom_ext import override


class DispatchEditPyCellWv(unohelper.Base, XDispatch):
    """If the View is not in PY_OBJ state the it is switched into PY_OBJ State."""

    def __init__(self, sheet: str, cell: str, in_thread: bool = False) -> None:
        super().__init__()
        self._sheet = sheet
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("init: sheet=%s, cell=%s", sheet, cell)
        self._in_thread = in_thread
        self._status_listeners: Dict[str, XStatusListener] = {}

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self._log.indent(True):
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

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        with self._log.indent(True):
            try:
                self._log.debug("dispatch(): url=%s", URL.Main)
                serv = cast(
                    Any,
                    Lo.create_instance_mcf(XInterface, "___lo_identifier___.py_edit_cell_job"),
                )
                nv_cell = NamedValue("cell", self._cell)
                nv_sheet = NamedValue("sheet", self._sheet)
                serv.execute((nv_cell, nv_sheet))
                return

            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error("Error: %s", e, exc_info=True)
                return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        Un-registers a listener from a control.
        """
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]
