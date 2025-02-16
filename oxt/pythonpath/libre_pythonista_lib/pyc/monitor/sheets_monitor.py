from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.events.partial.events_partial import EventsPartial

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import SHEET_MODIFIED
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import SHEET_MODIFIED


class SheetsMonitor(EventsPartial):
    def __init__(self) -> None:
        EventsPartial.__init__(self)
        self._shared_event = SharedEvent()
        self._shared_event.add_event_observers(self.event_observer)
