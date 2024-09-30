"""
Startup Named Events.
"""

from __future__ import annotations
from typing import NamedTuple


class StartupNamedEvent(NamedTuple):
    """
    Named events for startup
    """

    WINDOW_STARTED = "startup_window_started"
    """Event triggered when LibreOffice window first starts."""
