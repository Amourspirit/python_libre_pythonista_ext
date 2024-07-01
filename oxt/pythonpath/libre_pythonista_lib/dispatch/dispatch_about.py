from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL

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

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        if url.Complete in self._status_listeners:
            self._log.debug(f"addStatusListener(): url={url.Main} already exists.")
        else:
            self._status_listeners[url.Complete] = control

    def dispatch(self, url: URL, args: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        try:
            self._log.debug(f"dispatch(): url={url.Main}")
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

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        if url.Complete in self._status_listeners:
            del self._status_listeners[url.Complete]
