from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING

from ooodev.loader import Lo
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..const.event_const import GBL_DOC_CLOSING
from ..ex.exceptions import SingletonKeyError
from .doc_event_partial import DocEventPartial

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT


class SharedEvent(DocEventPartial):
    _instances: Dict[str, SharedEvent] = {}

    def __new__(cls, doc: OfficeDocumentT | None = None) -> SharedEvent:
        if doc is None:
            eargs = EventArgs(cls)
            eargs.event_data = DotDict(class_name=cls.__name__, doc=None)
            LoEvents().trigger("LibrePythonistaSharedEventGetDoc", eargs)
            if eargs.event_data.doc is not None:
                doc = eargs.event_data.doc
            if doc is None:
                try:
                    doc = Lo.current_doc
                except Exception as e:
                    raise SingletonKeyError(
                        f"Error getting single key for class name: {cls.__name__}"
                    ) from e

        key = f"doc_{doc.runtime_uid}"
        if key not in cls._instances:
            inst = super(SharedEvent, cls).__new__(cls)
            inst._is_init = False
            inst.__init__(doc)
            cls._instances[key] = inst

        return cls._instances[key]

    def __init__(self, doc: OfficeDocumentT | None = None) -> None:
        if getattr(self, "_is_init", True):
            return
        DocEventPartial.__init__(self, doc=doc)
        # self._doc = doc
        self._is_init = True


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"doc_{uid}"
    if key in SharedEvent._instances:
        del SharedEvent._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
