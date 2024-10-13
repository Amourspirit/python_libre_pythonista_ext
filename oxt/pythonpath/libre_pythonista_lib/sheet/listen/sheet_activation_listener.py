from __future__ import annotations
from typing import Any, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
import unohelper
from com.sun.star.sheet import XActivationEventListener
from ooodev.loader import Lo
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ...const.event_const import GBL_DOC_CLOSING
from ...const.event_const import SHEET_ACTIVATION
from ...event.shared_event import SharedEvent

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


# is added when document view is complete.


class SheetActivationListener(XActivationEventListener, unohelper.Base):
    """Singleton Class for Sheet Activation Listener."""

    _instances = {}

    def __new__(cls) -> SheetActivationListener:
        key = cls._get_key()
        if key not in cls._instances:
            inst = super().__new__(cls)
            inst._is_init = False
            cls._instances[key] = inst
        return cls._instances[key]

    @classmethod
    def _get_key(cls) -> str:
        return f"{Lo.current_doc.runtime_uid}_uid"

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        XActivationEventListener.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._is_init = True

    @override
    def activeSpreadsheetChanged(self, aEvent: ActivationEvent) -> None:
        """
        Is called whenever data or a selection changed.

        This interface must be implemented by components that wish to get notified of changes of the active Spreadsheet. They can be registered at an XSpreadsheetViewEventProvider component.

        **since**

            OOo 2.0
        """
        self._log.debug("activeSpreadsheetChanged")
        eargs = EventArgs(self)
        eargs.event_data = DotDict(sheet=aEvent.ActiveSheet, event=aEvent)
        se = SharedEvent()
        se.trigger_event(SHEET_ACTIVATION, eargs)

    @override
    def disposing(self, Source: EventObject) -> None:
        """
        gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including XComponent.removeEventListener() ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at XComponent.
        """
        if self._log is not None:
            self._log.debug("Disposing")
        setattr(self, "_log", None)  # avoid type checker complaining about log being none.

    def __del__(self) -> None:
        if self._log is not None:
            self._log.debug("Deleted")
        setattr(self, "_log", None)


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"{uid}_uid"
    if key in SheetActivationListener._instances:
        del SheetActivationListener._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
