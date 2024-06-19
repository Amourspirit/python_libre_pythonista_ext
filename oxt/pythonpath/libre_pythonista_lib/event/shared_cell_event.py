from __future__ import annotations
from typing import Any, List, Dict, Tuple, TYPE_CHECKING

from ooodev.calc import CalcDoc
from ooodev.events.partial.events_partial import EventsPartial


class SharedCellEvent(EventsPartial):
    _instances: Dict[str, SharedCellEvent] = {}

    def __new__(cls, doc: CalcDoc | None = None) -> SharedCellEvent:
        if doc is None:
            doc = CalcDoc.from_current_doc()
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            cls._instances[key] = super(SharedCellEvent, cls).__new__(cls)
            cls._instances[key]._is_init = False
        return cls._instances[key]

    def __init__(self, doc: CalcDoc | None = None) -> None:
        if getattr(self, "_is_init", True):
            return
        EventsPartial.__init__(self)
        # self._doc = doc
        self._is_init = True
