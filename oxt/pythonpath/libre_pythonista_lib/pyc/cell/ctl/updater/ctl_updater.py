from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.events.partial.events_partial import EventsPartial

from .ctl_provider import CtlProvider

if TYPE_CHECKING:
    from ..ctl_t import CtlT


class CtlUpdater(EventsPartial):
    def __init__(self, ctl: CtlT, provider: CtlProvider | None) -> None:
        EventsPartial.__init__(self)
        if provider is None:
            from .ctl_provider_default import CtlProviderDefault

            provider = CtlProviderDefault(ctl)
        self._provider = provider
        self._provider.add_event_observers(self.event_observer)

    @property
    def provider(self) -> CtlProvider:
        return self._provider
