from __future__ import annotations
from typing import Any
from ...meta.singleton import Singleton
from ...oxt_logger import OxtLogger
from ...events.lo_events import LoEvents
from ...events.args.event_args import EventArgs
from ...events.named_events.startup_events import StartupNamedEvent


class StartupMonitor(metaclass=Singleton):
    """Singleton class to monitor startup progress."""

    def __init__(self) -> None:
        self._logger = OxtLogger(log_name=__name__)
        self._window_started = False

        def on_window_started(source: Any, event: EventArgs) -> None:
            self._logger.debug("Window started.")
            self._window_started = True

        self._fn_on_window_started = on_window_started
        events = LoEvents()
        events.on(StartupNamedEvent.WINDOW_STARTED, self._fn_on_window_started)

    # region Properties
    @property
    def window_started(self) -> bool:
        """Gets if window started event has taken place."""
        return self._window_started

    # endregion Properties
