from __future__ import annotations
from typing import Any, Dict

from ooodev.calc import CalcDoc
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ..const.event_const import GBL_DOC_CLOSING


class SharedEvent(EventsPartial):
    _instances: Dict[str, SharedEvent] = {}

    def __new__(cls, doc: CalcDoc | None = None) -> SharedEvent:
        if doc is None:
            doc = CalcDoc.from_current_doc()
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            cls._instances[key] = super(SharedEvent, cls).__new__(cls)
            cls._instances[key]._is_init = False
        return cls._instances[key]

    def __init__(self, doc: CalcDoc | None = None) -> None:
        if getattr(self, "_is_init", True):
            return
        EventsPartial.__init__(self)
        # self._doc = doc
        self._is_init = True


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"doc_{uid}"
    if key in SharedEvent._instances:
        del SharedEvent._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
