# coding: utf-8
"""
Internal Module only! DO NOT use this module/class!

This module is for the purpose of sharing events between classes internally
"""

from __future__ import annotations
import contextlib
from weakref import ref, ReferenceType
from .args.event_args import EventArgs, AbstractEvent
from typing import List, Dict, Union, cast
from ..lo_util import type_var
from ..proto import event_observer


class _Events(object):
    """
    Singleton Class for sharing events among internal classes. DO NOT USE!

    Use: lo_events.LoEvents for global events. Use lo_events.Events for locally scoped events.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_Events, cls).__new__(cls, *args, **kwargs)
            cls._instance._callbacks = None
            cls._instance._observers = None
        return cls._instance

    def __init__(self, *args, **kwargs):
        self._callbacks: Union[Dict[str, List[ReferenceType[type_var.EventCallback]]], None]
        self._observers: Union[List[ReferenceType[event_observer.EventObserver]], None]

    def on(self, event_name: str, callback: type_var.EventCallback):
        """
        Registers an event

        Args:
            event_name (str): Unique event name
            callback (Callable[[object, EventArgs], None]): Callback function
        """
        if self._callbacks is None:
            self._callbacks = {}

        if event_name not in self._callbacks:
            self._callbacks[event_name] = [ref(callback)]
        else:
            self._callbacks[event_name].append(ref(callback))

    def trigger(self, event_name: str, event_args: AbstractEvent, *args, **kwargs) -> None:
        """
        Trigger event(s) for a given name.

        Args:
            event_name (str): Name of event to trigger/
            event_args (AbstractEvent): Event args passed to the callback for trigger.
            args (Any, optional): Optional positional args to pass to callback
            kwargs (Any, optional): Optional keyword args to pass to callback
        """
        if self._callbacks is not None and event_name in self._callbacks:
            cleanup = None
            for i, callback in enumerate(self._callbacks[event_name]):
                if callback() is None:
                    if cleanup is None:
                        cleanup = []
                    cleanup.append(i)
                    continue
                if event_args is not None:
                    event_args._event_name = event_name
                    if event_args.event_source is None:
                        event_args._event_source = self  # type: ignore
                if callable(callback()):
                    try:
                        callback()(event_args.source, event_args, *args, **kwargs)  # type: ignore
                    except AttributeError:
                        # event_arg is None
                        callback()(self, None)  # type: ignore
            if cleanup:
                # reverse list to allow removing form highest to lowest to avoid errors
                cleanup.reverse()
                for i in cleanup:
                    self._callbacks[event_name].pop(i)
                if len(self._callbacks[event_name]) == 0:
                    del self._callbacks[event_name]
        self._update_observers(event_name, event_args)  # type: ignore

    def _update_observers(self, event_name: str, event_args: EventArgs) -> None:
        # sourcery skip: last-if-guard
        if self._observers is not None:
            cleanup = None
            for i, observer in enumerate(self._observers):
                if observer() is None:
                    if cleanup is None:
                        cleanup = []
                    cleanup.append(i)
                    continue
                observer().trigger(event_name=event_name, event_args=event_args)  # type: ignore
            if cleanup:
                # reverse list to allow removing form highest to lowest to avoid errors
                cleanup.reverse()
                for i in cleanup:
                    self._observers.pop(i)

    def add_observer(self, *args: event_observer.EventObserver) -> None:
        """
        Adds observers that gets their ``trigger`` method called when this class ``trigger`` method is called.
        """
        if self._observers is None:
            self._observers = []
        for observer in args:
            self._observers.append(ref(observer))

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
        if self._callbacks is None:
            return False
        result = False
        if event_name in self._callbacks:
            # cb = cast(Dict[str, List[EventCallback]], self._callbacks)
            with contextlib.suppress(ValueError):
                self._callbacks[event_name].remove(ref(callback))
                result = True
        return result
