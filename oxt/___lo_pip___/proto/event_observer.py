from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Protocol
else:
    Protocol = object

from ..lo_util import type_var
from ..events.args import event_args


class EventObserver(Protocol):
    """
    Protocol Class for Event Observer.

    See Also:
        :py:mod:`~.events.lo_events`
    """

    def on(self, event_name: str, callback: type_var.EventCallback):
        """
        Registers an event

        Args:
            event_name (str): Unique event name
            callback (Callable[[object, EventArgs], None]): Callback function
        """
        ...

    def remove(self, event_name: str, callback: type_var.EventCallback) -> bool:
        """
        Removes an event callback

        Args:
            event_name (str): Unique event name
            callback (Callable[[object, EventArgs], None]): Callback function

        Returns:
            bool: True if callback has been removed; Otherwise, False.
            False means the callback was not found.
        """
        ...

    def trigger(self, event_name: str, event_args: event_args.AbstractEvent):
        """
        Trigger event(s) for a given name.

        Args:
            event_name (str): Name of event to trigger
            event_args (EventArgs): Event args passed to the callback for trigger.
        """
        ...
