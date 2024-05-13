from __future__ import annotations
from typing import Any
from .key_val_args import AbstractKeyValArgs
from .cancel_event_args import AbstractCancelEventArgs


class AbstractKeyValueArgs(AbstractKeyValArgs, AbstractCancelEventArgs):
    __slots__ = ()

    def __init__(self, source: Any, key: str, value: Any, cancel=False) -> None:
        """
        Constructor

        Args:
            source (Any): Event Source
            key (str): Key
            value (Any: Value
        """
        super().__init__(source=source, key=key, value=value)
        self.cancel = cancel
        self.default = False
        self.handled = False


class KeyValCancelArgs(AbstractKeyValueArgs):
    """
    Key Value Cancel Args

    .. versionadded:: 0.9.0
    """

    __slots__ = (
        "key",
        "value",
        "source",
        "_event_name",
        "event_data",
        "cancel",
        "handled",
        "_event_source",
        "_kv_data",
        "default",
    )

    @staticmethod
    def from_args(args: AbstractKeyValueArgs) -> KeyValCancelArgs:
        """
        Gets a new instance from existing instance

        Args:
            args (AbstractKeyValueArgs): Existing Instance

        Returns:
            KeyValCancelArgs: args
        """
        event_args = KeyValCancelArgs(source=args.source, key=args.key, value=args.value)
        event_args.default = args.default
        event_args._event_name = args.event_name
        event_args._event_source = args.event_source
        event_args.event_data = args.event_data
        event_args.cancel = args.cancel
        event_args.handled = args.handled
        return event_args
