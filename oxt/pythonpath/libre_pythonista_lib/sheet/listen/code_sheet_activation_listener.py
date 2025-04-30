from __future__ import annotations
from typing import Any, Generator, TYPE_CHECKING
import contextlib

import unohelper
from com.sun.star.sheet import XActivationEventListener
from ooodev.calc import CalcDoc

if TYPE_CHECKING:
    from typing_extensions import override
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from oxt.pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.sheet_event_mgr import SheetEventMgr
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
else:
    from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.doc.calc.doc.sheet.sheet_event_mgr import SheetEventMgr
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin

    def override(func: Any) -> Any:  # noqa: ANN401
        return func


_KEY = "libre_pythonista_lib.sheet.listen.code_sheet_activation_listener.CodeSheetActivationListener"


class CodeSheetActivationListener(XActivationEventListener, LogMixin, TriggerStateMixin, unohelper.Base):
    """
    Singleton Class for Sheet Activation Listener.

    Automatically adds a Modify Listener to the sheet when activated if it does not already have one.
    """

    def __new__(cls) -> CodeSheetActivationListener:
        gbl_cache = DocGlobals.get_current()
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        XActivationEventListener.__init__(self)
        LogMixin.__init__(self)
        TriggerStateMixin.__init__(self)
        unohelper.Base.__init__(self)
        self._is_init = True

    @override
    def activeSpreadsheetChanged(self, aEvent: ActivationEvent) -> None:  # noqa: N802, N803
        """
        is called whenever data or a selection changed.

        This interface must be implemented by components that wish to get notified of changes of the active Spreadsheet. They can be registered at an XSpreadsheetViewEventProvider component.

        **since**

            OOo 2.0
        """
        self.log.debug("activeSpreadsheetChanged")
        if not self.is_trigger():
            self.log.debug("activeSpreadsheetChanged() Trigger events is False. Returning.")
            return
        doc = CalcDoc.from_current_doc()
        sheet = doc.sheets.get_sheet(aEvent.ActiveSheet)
        unique_id = sheet.unique_id
        _ = SheetEventMgr(sheet)
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
        # do not remove from cache when disposing.
        # in some cased the listener is removed and then added again to ensure the listener is active.
        # This may cause disposing to be called.
        # If the listener is removed from the cache, it will not be added again but as a new instance.
        # This would not be a true singleton and that leads to side effects.
        pass
        # with contextlib.suppress(Exception):
        #     gbl_cache = DocGlobals.get_current()
        #     if _KEY in gbl_cache.mem_cache:
        #         del gbl_cache.mem_cache[_KEY]

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if _KEY in gbl_cache.mem_cache:
                del gbl_cache.mem_cache[_KEY]
