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
from ooodev.calc import CalcDoc
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from .code_sheet_modify_listener import CodeSheetModifyListener
from ...const.event_const import GBL_DOC_CLOSING
from ...sheet.calculate import set_doc_sheets_calculate_event

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class SheetCalculationEventListener(unohelper.Base, XActivationEventListener):
    """Singleton Class for Sheet Activation Listener."""

    _instances = {}

    def __new__(cls) -> SheetCalculationEventListener:
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
        super().__init__()
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
        doc = CalcDoc.from_current_doc()
        try:
            set_doc_sheets_calculate_event(doc)
        except Exception as e:
            self._log.error("Error setting document sheets calculate event", exc_info=True)

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
    if key in SheetCalculationEventListener._instances:
        del SheetCalculationEventListener._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
