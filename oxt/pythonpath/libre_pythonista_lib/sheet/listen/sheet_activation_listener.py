from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper
from com.sun.star.sheet import XActivationEventListener
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import SHEET_ACTIVATION
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.const.event_const import SHEET_ACTIVATION
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from libre_pythonista_lib.log.log_mixin import LogMixin

# is added when document view is complete.
_KEY = "libre_pythonista_lib.sheet.listen.sheet_activation_listener.SheetActivationListener"


class SheetActivationListener(XActivationEventListener, LogMixin, TriggerStateMixin, unohelper.Base):
    """Singleton Class for Sheet Activation Listener."""

    def __new__(cls) -> SheetActivationListener:
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
    def activeSpreadsheetChanged(self, aEvent: ActivationEvent) -> None:  # noqa: N803
        """
        Is called whenever data or a selection changed.

        This interface must be implemented by components that wish to get notified of changes of the active Spreadsheet. They can be registered at an XSpreadsheetViewEventProvider component.

        **since**

            OOo 2.0
        """
        self.log.debug("activeSpreadsheetChanged")
        if not self.is_trigger():
            self.log.debug("Trigger events is False. Not raising SHEET_ACTIVATION event.")
            return

        eargs = EventArgs(self)
        eargs.event_data = DotDict(sheet=aEvent.ActiveSheet, event=aEvent)
        se = SharedEvent()
        se.trigger_event(SHEET_ACTIVATION, eargs)

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
