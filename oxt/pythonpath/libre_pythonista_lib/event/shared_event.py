from __future__ import annotations
from typing import TYPE_CHECKING, Optional

# from ooodev.loader import Lo
# from ooodev.events.lo_events import LoEvents
# from ooodev.events.args.event_args import EventArgs
# from ooodev.events.lo_events import LoEvents
# from ooodev.events.args.event_args import EventArgs
# from ooodev.utils.helper.dot_dict import DotDict

# from ..const.event_const import GBL_DOC_CLOSING
# from ..ex.exceptions import SingletonKeyError

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ooodev.events.args.event_args_t import EventArgsT
    from ooodev.utils.type_var import EventCallback
    from oxt.pythonpath.libre_pythonista_lib.event.doc_event_partial import DocEventPartial
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.___lo_pip___.basic_config import BasicConfig

else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.event.doc_event_partial import DocEventPartial
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista.basic_config import BasicConfig

_KEY = "libre_pythonista_lib.event.shared_event.SharedEvent"


class SharedEvent(DocEventPartial, LogMixin):
    def __new__(cls, doc: Optional[OfficeDocumentT] = None) -> SharedEvent:
        gbl_cache = DocGlobals.get_current() if doc is None else DocGlobals.get_current(doc.runtime_uid)
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super(SharedEvent, cls).__new__(cls)
        inst._is_init = False
        inst.__init__(doc)
        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self, doc: Optional[OfficeDocumentT] = None) -> None:
        if getattr(self, "_is_init", True):
            return
        DocEventPartial.__init__(self, doc=doc)
        LogMixin.__init__(self)
        self.log.debug("Init")
        self._config = BasicConfig()
        self._is_init = True

    def trigger_event(self, event_name: str, event_args: EventArgsT) -> None:
        """
        Trigger an event on current instance.

        Args:
            event_name (str): Event Name.
            event_args (EventArgsT): Event Args.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:
        """
        if self.log.is_debug and event_name in self._config.debug_skip_events:
            self.log.warning("trigger_event() event_name: %s is in debug_skip_events. Skipping.", event_name)
            return
        self.log.debug("trigger_event() event_name: %s", event_name)
        DocEventPartial.trigger_event(self, event_name, event_args)

    def subscribe_event(self, event_name: str, callback: EventCallback) -> None:
        """
        Add an event listener to current instance.

        Args:
            event_name (str): Event Name.
            callback (EventCallback): Callback of the event listener.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:
        """
        self.log.debug("subscribe_event() event_name: %s", event_name)
        DocEventPartial.subscribe_event(self, event_name, callback)

    def unsubscribe_event(self, event_name: str, callback: EventCallback) -> None:
        """
        Remove an event listener from current instance.

        Args:
            event_name (str): Event Name.
            callback (EventCallback): Callback of the event listener.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:
        """
        self.log.debug("unsubscribe_event() event_name: %s", event_name)
        DocEventPartial.unsubscribe_event(self, event_name, callback)
