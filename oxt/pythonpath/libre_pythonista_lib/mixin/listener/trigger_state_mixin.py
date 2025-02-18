from __future__ import annotations
from typing import Generator
import contextlib


class TriggerStateMixin:
    def __init__(self) -> None:
        self.__trigger_state = True

    def set_trigger_state(self, trigger: bool) -> None:
        """
        Sets the state of the trigger events.

        Args:
            trigger (bool): The state to set for the trigger events. If True,
                trigger events will be enabled. If False, they will be disabled.
        Returns:
            None
        """
        self.__trigger_state = trigger

    def get_trigger_state(self) -> bool:
        """
        Gets the state of the trigger events.

        Returns:
            bool: The state of the trigger events.
        """
        return self.__trigger_state

    def is_trigger(self) -> bool:
        """
        Returns whether trigger events are enabled.

        Returns:
            bool: True if trigger events are enabled, otherwise False.
        """
        return self.__trigger_state is True

    @contextlib.contextmanager
    def trigger_context(self, trigger: bool = False) -> Generator[None, None, None]:
        """
        Context manager for temporarily changing the trigger state.

        Args:
            trigger (bool, optional): The state to set for the trigger events within the context.
                Defaults to False.
        """
        original_state = self.get_trigger_state()
        self.set_trigger_state(trigger)
        try:
            yield
        finally:
            self.set_trigger_state(original_state)
