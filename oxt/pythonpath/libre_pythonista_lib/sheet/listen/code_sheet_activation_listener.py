from __future__ import annotations
from typing import Any, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper
from com.sun.star.sheet import XActivationEventListener
from ooodev.calc import CalcDoc
from .code_sheet_modify_listener import CodeSheetModifyListener

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.log.log_mixin import LogMixin

_CODE_SHEET_ACTIVATION_LISTENER_KEY = (
    "libre_pythonista_lib.sheet.listen.code_sheet_activation_listener.CodeSheetActivationListener"
)


class CodeSheetActivationListener(XActivationEventListener, LogMixin, unohelper.Base):
    """Singleton Class for Sheet Activation Listener."""

    def __new__(cls) -> CodeSheetActivationListener:
        gbl_cache = DocGlobals.get_current()
        if _CODE_SHEET_ACTIVATION_LISTENER_KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_CODE_SHEET_ACTIVATION_LISTENER_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_CODE_SHEET_ACTIVATION_LISTENER_KEY] = inst
        return inst

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        XActivationEventListener.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self._is_init = True

    @override
    def activeSpreadsheetChanged(self, aEvent: ActivationEvent) -> None:  # noqa: N803
        """
        is called whenever data or a selection changed.

        This interface must be implemented by components that wish to get notified of changes of the active Spreadsheet. They can be registered at an XSpreadsheetViewEventProvider component.

        **since**

            OOo 2.0
        """
        self.log.debug("activeSpreadsheetChanged")
        doc = CalcDoc.from_current_doc()
        sheet = doc.sheets.get_sheet(aEvent.ActiveSheet)
        unique_id = sheet.unique_id
        if not CodeSheetModifyListener.has_listener(unique_id):
            self.log.debug("Adding Modify Listener to sheet with unique id of: %s", unique_id)
            listener = CodeSheetModifyListener(unique_id)  # singleton
            sheet.component.addModifyListener(listener)
        else:
            self.log.debug("Sheet with unique id of: %s already has a Modify Listener", unique_id)

    @override
    def disposing(self, Source: EventObject) -> None:  # noqa: N803
        """
        gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including XComponent.removeEventListener() ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at XComponent.
        """
        gbl_cache = DocGlobals.get_current()
        if _CODE_SHEET_ACTIVATION_LISTENER_KEY in gbl_cache.mem_cache:
            del gbl_cache.mem_cache[_CODE_SHEET_ACTIVATION_LISTENER_KEY]

    def __del__(self) -> None:
        gbl_cache = DocGlobals.get_current()
        if _CODE_SHEET_ACTIVATION_LISTENER_KEY in gbl_cache.mem_cache:
            del gbl_cache.mem_cache[_CODE_SHEET_ACTIVATION_LISTENER_KEY]
