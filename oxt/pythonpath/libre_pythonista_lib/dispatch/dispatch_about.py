from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.utils.string.str_list import StrList
from ooodev.dialog.msgbox import MsgBox, MessageBoxType
from ooodev.loader import Lo

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class DispatchAbout(unohelper.Base, XDispatch):
    """If the View is not in PY_OBJ state the it is switched into PY_OBJ State."""

    def __init__(self):
        super().__init__()
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._status_listeners: Dict[str, XStatusListener] = {}

    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        # https://wiki.openoffice.org/wiki/Documentation/DevGuide/WritingUNO/Implementation
        with self._log.indent(True):
            if URL.Complete in self._status_listeners:
                self._log.debug(f"addStatusListener(): url={URL.Main} already exists.")
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # setting State will affect how the control is displayed in menus.
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=URL, IsEnabled=True, State=None)
                Control.statusChanged(fe)
                self._status_listeners[URL.Complete] = Control

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
                _ = Lo.current_doc
                rr = ResourceResolver(Lo.get_context())
                cfg = Config()
                sl = StrList(sep="\n")
                for author in cfg.author_names:
                    sl.append(f"by {author}")
                msg = f"{cfg.extension_display_name}"
                msg += "\n" + rr.resolve_string("strVersion")
                msg += f" {cfg.extension_version}"
                lic = rr.resolve_string("strExtensionUnderLic").format(cfg.extension_license)
                msg += "\n" + lic
                if len(sl) > 0:
                    msg += "\n" + str(sl)
                _ = MsgBox.msgbox(
                    msg=msg,
                    title=rr.resolve_string("mbTitleAbout"),
                    boxtype=MessageBoxType.INFOBOX,
                )
                return

            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error(f"Error: {e}", exc_info=True)
                return

    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]
