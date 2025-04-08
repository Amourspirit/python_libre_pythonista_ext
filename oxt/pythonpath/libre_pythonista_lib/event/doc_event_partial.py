from __future__ import annotations
from contextlib import contextmanager
from typing import Set, TYPE_CHECKING

from ooodev.loader import Lo
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

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
        if doc is None:
            raise ValueError("doc cannot be None")
        self.__runtime_uid = doc.runtime_uid
        self.__omit_events: Set[str] = set()
        EventsPartial.__init__(self)

    def __check_runtime_uid(self) -> bool:
        eargs = EventArgs(self)
        eargs.event_data = DotDict(current_udi=self.__runtime_uid, doc_uid="")
        LoEvents().trigger("LibrePythonistaDocEventPartialCheckUid", eargs)
        if eargs.event_data.doc_uid:
            return eargs.event_data.doc_uid == self.__runtime_uid
        if Lo.current_doc is None:
            return False
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
                if event_name not in self.__omit_events:
                    EventsPartial.trigger_event(self, event_name, event_args)
        except Exception as e:
            raise RuntimeUidError(f"Error checking runtime_uid: {e}") from e

    # endregion EventsPartial Overrides
    @contextmanager
    def suspend_event_context(self, *event_names: str):
        """
        Context manager that on entry adds events to the omit list.
        On exit removes events from the omit list.
        """
        try:
            for event_name in event_names:
                self.__omit_events.add(event_name)
            yield
        finally:
            for event_name in event_names:
                self.__omit_events.discard(event_name)
