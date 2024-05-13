from __future__ import annotations
from typing import Any
from .event_args import AbstractEvent


class AbstractKeyValArgs(AbstractEvent):
    # https://stackoverflow.com/questions/472000/usage-of-slots
    __slots__ = ()

    def __init__(self, source: Any, key: str, value: Any) -> None:
        """
        Constructor

        Args:
            source (Any): Event Source
            key (str): Key
            value (Any: Value
        """
        super().__init__(source)
        self.key = key
        self.value = value
        self.default = False

    cmd: str
    """Gets/Sets the dispatch cmd of the event"""


class KeyValArgs(AbstractKeyValArgs):
    """
    Key Value Args

    .. versionadded:: 0.9.0
    """

    __slots__ = ("source", "_event_name", "event_data", "key", "value", "_event_source", "_kv_data", "default")

    @staticmethod
    def from_args(args: AbstractKeyValArgs) -> KeyValArgs:
        """
        Gets a new instance from existing instance

        Args:
            args (KeyValArgs): Existing Instance

        Returns:
            KeyValArgs: args
        """
        event_args = KeyValArgs(source=args.source, key=args.key, value=args.value)
        event_args.default = args.default
        event_args._event_name = args.event_name
        event_args._event_source = args.event_source
        event_args.event_data = args.event_data
        return event_args
