from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.loader import Lo
from ooodev.events.partial.events_partial import EventsPartial
from ..ex import RuntimeUidError

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ooodev.utils.type_var import EventCallback
    from ooodev.events.args.event_args_t import EventArgsT
    from ooodev.proto.event_observer import EventObserver


class DocEventPartial(EventsPartial):

    def __init__(self, doc: OfficeDocumentT | None = None) -> None:
        if doc is None:
            doc = Lo.current_doc
        self.__runtime_uid = doc.runtime_uid
        EventsPartial.__init__(self)

    def __check_runtime_uid(self) -> bool:
        return Lo.current_doc.runtime_uid == self.__runtime_uid

    # region EventsPartial Overrides
    def add_event_observers(self, *args: EventObserver) -> None:
        """
        Adds observers that gets their ``trigger`` method called when this class ``trigger`` method is called.

        Parameters:
            args (EventObserver): One or more observers to add.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:

        Note:
            Observers are removed automatically when they are out of scope.
        """
        try:
            if self.__check_runtime_uid():
                EventsPartial.add_event_observers(self, *args)
        except Exception as e:
            raise RuntimeUidError(f"Error checking runtime_uid: {e}") from e

    def remove_event_observer(self, observer: EventObserver) -> bool:
        """
        Removes an observer

        Args:
            observer (EventObserver): One or more observers to add.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            bool: ``True`` if observer has been removed; Otherwise, ``False``.
        """
        try:
            if self.__check_runtime_uid():
                return EventsPartial.remove_event_observer(self, observer)
            else:
                raise RuntimeUidError("Runtime UID does not match")
        except Exception as e:
            raise RuntimeUidError(f"Error checking runtime_uid: {e}") from e

    def subscribe_event(self, event_name: str, callback: EventCallback) -> None:
        """
        Add an event listener to current instance.

        Args:
            event_name (str): Event Name.
            callback (EventCallback): Callback of the event listener.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:
        """
        try:
            if self.__check_runtime_uid():
                EventsPartial.subscribe_event(self, event_name, callback)
        except Exception as e:
            raise RuntimeUidError(f"Error checking runtime_uid: {e}") from e

    def unsubscribe_event(self, event_name: str, callback: EventCallback) -> None:
        """
        Remove an event listener from current instance.

        Args:
            event_name (str): Event Name.
            callback (EventCallback): Callback of the event listener.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:
        """
        try:
            if self.__check_runtime_uid():
                EventsPartial.unsubscribe_event(self, event_name, callback)
        except Exception as e:
            raise RuntimeUidError(f"Error checking runtime_uid: {e}") from e

    def trigger_event(self, event_name: str, event_args: EventArgsT):
        """
        Trigger an event on current instance.

        Args:
            event_name (str): Event Name.
            event_args (EventArgsT): Event Args.

        Raises:
            RuntimeUidError: If the runtime_uid check fails.

        Returns:
            None:
        """
        try:
            if self.__check_runtime_uid():
                EventsPartial.trigger_event(self, event_name, event_args)
        except Exception as e:
            raise RuntimeUidError(f"Error checking runtime_uid: {e}") from e

    # endregion EventsPartial Overrides
