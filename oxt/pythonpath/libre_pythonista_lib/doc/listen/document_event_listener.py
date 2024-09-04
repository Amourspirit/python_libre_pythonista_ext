from __future__ import annotations
from typing import Any, TYPE_CHECKING

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
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DocumentEventListener(XDocumentEventListener, unohelper.Base):
    """Singleton class for Document Event Listener."""

    _instances = {}

    def __new__(cls) -> DocumentEventListener:
        key = cls._get_key()
        if key not in cls._instances:
            inst = super().__new__(cls)
            inst._is_init = False
            inst._inst_name = key
            cls._instances[key] = inst
        return cls._instances[key]

    @classmethod
    def _get_key(cls) -> str:
        return f"{Lo.current_doc.runtime_uid}_uid_{cls.__name__}"

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        XDocumentEventListener.__init__(self)
        unohelper.Base.__init__(self)
        self._inst_name: str  # = inst_name
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init")
        self._uid = Lo.current_doc.runtime_uid
        self._shared_event = SharedEvent()
        self._is_init = True

    def documentEventOccured(self, event: DocumentEvent) -> None:
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
        self._log.debug(f"Document Event Occurred: {event.EventName}")
        eargs = EventArgs(self)
        dd = DotDict(run_id=self._uid, event_name=event.EventName)
        eargs.event_data = dd
        self._shared_event.trigger_event(DOCUMENT_EVENT, eargs)

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
        if self._inst_name in DocumentEventListener._instances:
            del DocumentEventListener._instances[self._inst_name]
        setattr(self, "_log", None)  # avoid type checker complaining about
