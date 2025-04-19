from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
import unohelper
from com.sun.star.document import XDocumentEventListener

from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ...event.shared_event import SharedEvent
from ...const.event_const import DOCUMENT_EVENT

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.document import DocumentEvent
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.log.log_mixin import LogMixin

_DOCUMENT_EVENT_LISTENER_KEY = "libre_pythonista_lib.doc.listen.document_event_listener.DocumentEventListener"


class DocumentEventListener(XDocumentEventListener, LogMixin, unohelper.Base):
    """Singleton class for Document Event Listener."""

    def __new__(cls) -> DocumentEventListener:
        gbl_cache = DocGlobals.get_current()
        if _DOCUMENT_EVENT_LISTENER_KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_DOCUMENT_EVENT_LISTENER_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_DOCUMENT_EVENT_LISTENER_KEY] = inst
        return inst

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        XDocumentEventListener.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self.log.debug("Init")
        assert Lo.current_doc is not None
        self._uid = Lo.current_doc.runtime_uid
        self._trigger_events = True
        self._shared_event = SharedEvent()
        self._is_init = True

    def set_trigger_state(self, trigger: bool) -> None:
        """
        Sets the state of the trigger events.

        Args:
            trigger (bool): The state to set for the trigger events. If True,
                trigger events will be enabled. If False, they will be disabled.
        Returns:
            None
        """
        self._trigger_events = trigger

    def get_trigger_state(self) -> bool:
        """
        Returns the current state of the trigger events.

        Returns:
            bool: The state of the trigger events.
        """

        return self._trigger_events

    @override
    def documentEventOccured(self, Event: DocumentEvent) -> None:  # noqa: N803
        """
        Is called whenever a document event occurred
        """
        # - OnTitleChanged
        # - OnModifyChanged
        # - OnLoad
        # - OnPrepareViewClosing
        # - OnPrepareUnload
        # - OnModeChanged
        # - OnViewClosed
        # - OnUnload
        # - OnUnfocus
        # - OnTitleChanged
        # and more. See: https://ask.libreoffice.org/t/extension-run-on-libreoffice-startup/94512
        if not self._trigger_events:
            self.log.debug("Trigger events is False. Not raising DOCUMENT_EVENT event.")
            return

        self.log.debug("Document Event Occurred: %s", Event.EventName)
        eargs = EventArgs(self)
        dd = DotDict(run_id=self._uid, event_name=Event.EventName)
        eargs.event_data = dd
        self._shared_event.trigger_event(DOCUMENT_EVENT, eargs)

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

        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if _DOCUMENT_EVENT_LISTENER_KEY in gbl_cache.mem_cache:
                del gbl_cache.mem_cache[_DOCUMENT_EVENT_LISTENER_KEY]

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if _DOCUMENT_EVENT_LISTENER_KEY in gbl_cache.mem_cache:
                del gbl_cache.mem_cache[_DOCUMENT_EVENT_LISTENER_KEY]
