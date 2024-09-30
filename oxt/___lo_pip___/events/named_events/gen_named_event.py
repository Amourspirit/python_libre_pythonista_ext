"""
Startup Named Events.
"""

from __future__ import annotations
from typing import NamedTuple


class GenNamedEvent(NamedTuple):
    """
    Named events for startup
    """

    PROGRESS_RULES_EVENT = "progress_rules_event"
    """Event triggered when Progress rules are loading."""
