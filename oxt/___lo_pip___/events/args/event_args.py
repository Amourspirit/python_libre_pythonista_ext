from __future__ import annotations
from typing import Any
from abc import ABC
from ...lo_util.gen_util import NULL_OBJ


class AbstractEvent(ABC):
    # https://stackoverflow.com/questions/472000/usage-of-slots
    __slots__ = ()

    def __init__(self, source: Any) -> None:
        """
        Constructor

        Args:
            source (Any): Event Source
        """
        self.source = source
        self._event_name = ""
        self._event_source = None
        self.event_data = None
        self._kv_data = None

    source: Any
    """Gets/Sets Event source"""
    event_data: Any
    """Gets/Sets any extra data associated with the event"""

    def get(self, key: str, default: Any = NULL_OBJ) -> Any:
        """
        Gets user data from event.

        Args:
            key (str): Key used to store data
            default (Any, optional): Default value to return if ``key`` is not found.

        Returns:
            Any: Data for ``key`` if found; Otherwise, if ``default`` is set then ``default``.

        .. versionadded:: 0.9.0
        """
        if self._kv_data is None:
            if default is NULL_OBJ:
                raise KeyError(f'"{key}" not found. Maybe you want to include a default value.')
            return default
        if default is NULL_OBJ:
            return self._kv_data[key]
        return self._kv_data.get(key, default)

    def set(self, key: str, value: Any, allow_overwrite: bool = True) -> bool:
        """
        Sets a key value pair for event instance.

        Args:
            key (str): Key
            value (Any): Value
            allow_overwrite (bool, optional): If ``True`` and a ``key`` already exist then its ``value`` will be over written; Otherwise ``value`` will not be over written. Defaults to ``True``.

        Returns:
            bool: ``True`` if values is written; Otherwise, ``False``

        .. versionadded:: 0.9.0
        """
        if self._kv_data is None:
            self._kv_data = {}
        if allow_overwrite:
            self._kv_data[key] = value
            return True
        if key not in self._kv_data:
            self._kv_data[key] = value
            return True
        return False

    def has(self, key: str) -> bool:
        """
        Gets if a key exist in the instance

        Args:
            key (str): key

        Returns:
            bool: ``True`` if key exist; Otherwise ``False``

        .. versionadded:: 0.9.0
        """
        return False if self._kv_data is None else key in self._kv_data

    def remove(self, key: str) -> bool:
        """
        Removes key value pair from instance

        Args:
            key (str): key

        Returns:
            bool: ``True`` if key was found and removed; Otherwise, ``False``

        .. versionadded:: 0.9.0
        """
        if self._kv_data is None:
            return False
        if key in self._kv_data:
            del self._kv_data[key]
            return True
        return False

    @property
    def event_name(self) -> str:
        """
        Gets the event name for these args
        """
        return self._event_name

    @property
    def event_source(self) -> Any | None:
        """
        Gets the event source for these args
        """
        return self._event_source

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.event_name}>"


class EventArgs(AbstractEvent):
    """
    Event Arguments Class
    """

    __slots__ = ("source", "_event_name", "event_data", "_event_source", "_kv_data")

    @staticmethod
    def from_args(args: AbstractEvent) -> EventArgs:
        """
        Gets a new instance from existing instance

        Args:
            args (AbstractEvent): Existing Instance

        Returns:
            EventArgs: args
        """
        event_args = EventArgs(source=args.source)
        event_args._event_name = args.event_name
        event_args._event_source = args.event_source
        event_args.event_data = args.event_data
        return event_args
