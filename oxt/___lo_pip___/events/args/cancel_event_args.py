from __future__ import annotations
from typing import Any
from .event_args import AbstractEvent


class AbstractCancelEventArgs(AbstractEvent):
    # https://stackoverflow.com/questions/472000/usage-of-slots
    __slots__ = ()

    def __init__(self, source: Any, cancel=False) -> None:
        """
        Constructor

        Args:
            source (Any): Event Source
            cancel (bool, optional): Cancel value. Defaults to False.
        """
        super().__init__(source)
        self.cancel = cancel
        self.handled = False

    cancel: bool
    """Gets/Sets cancel value"""
    handled: bool
    """Get/Set Handled value. Typically if set to ``True`` then ``cancel`` is ignored."""


class CancelEventArgs(AbstractCancelEventArgs):
    """Cancel Event Arguments"""

    __slots__ = ("source", "_event_name", "event_data", "cancel", "handled", "_event_source", "_kv_data")

    @staticmethod
    def from_args(args: AbstractCancelEventArgs) -> CancelEventArgs:
        """
        Gets a new instance from existing instance

        Args:
            args (AbstractCancelEventArgs): Existing Instance

        Returns:
            CancelEventArgs: args
        """
        cancel_args = CancelEventArgs(source=args.source)
        cancel_args._event_name = args.event_name
        cancel_args._event_source = args.event_source
        cancel_args.event_data = args.event_data
        cancel_args.cancel = args.cancel
        cancel_args.handled = args.handled
        return cancel_args
