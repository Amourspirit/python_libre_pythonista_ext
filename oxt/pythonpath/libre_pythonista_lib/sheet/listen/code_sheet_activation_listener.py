from __future__ import annotations
from typing import TYPE_CHECKING

import uno
import unohelper
from com.sun.star.sheet import XActivationEventListener
from ooodev.calc import CalcDoc
from .code_sheet_modify_listener import CodeSheetModifyListener

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class CodeSheetActivationListener(unohelper.Base, XActivationEventListener):
    """Singleton Class for Sheet Activation Listener."""

    _instance = None

    def __new__(cls) -> CodeSheetActivationListener:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_init = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        super().__init__()
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._is_init = True

    def activeSpreadsheetChanged(self, event: ActivationEvent) -> None:
        """
        is called whenever data or a selection changed.

        This interface must be implemented by components that wish to get notified of changes of the active Spreadsheet. They can be registered at an XSpreadsheetViewEventProvider component.

        **since**

            OOo 2.0
        """
        self._log.debug("activeSpreadsheetChanged")
        doc = CalcDoc.from_current_doc()
        sheet = doc.sheets.get_sheet(event.ActiveSheet)
        unique_id = sheet.unique_id
        if not CodeSheetModifyListener.has_listener(unique_id):
            self._log.debug(f"Adding Modify Listener to sheet with unique id of: {unique_id}")
            listener = CodeSheetModifyListener(unique_id)  # singleton
            sheet.component.addModifyListener(listener)
        else:
            self._log.debug(f"Sheet with unique id of: {unique_id} already has a Modify Listener")

    def disposing(self, event: EventObject) -> None:
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
