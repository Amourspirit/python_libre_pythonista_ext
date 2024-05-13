"""
Configuration Named Events.
"""
from __future__ import annotations
from typing import NamedTuple


class LogNamedEvent(NamedTuple):
    """
    Named events for utils.lo.LO class
    """

    LOGGING_READY = "log_logging_ready"
    """Event triggered when logging is ready."""
