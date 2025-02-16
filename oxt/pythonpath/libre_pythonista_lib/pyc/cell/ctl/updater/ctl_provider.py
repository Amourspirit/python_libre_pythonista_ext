from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from ooodev.events.partial.events_partial import EventsPartial

if TYPE_CHECKING:
    from ..ctl_t import CtlT


class CtlProvider(EventsPartial, ABC):
    """Control Provider Interface"""

    def __init__(self, ctl: CtlT) -> None:
        EventsPartial.__init__(self)
        self.__ctl = ctl

    @abstractmethod
    def add_ctl(self) -> object | None:
        """
        Adds a control to the cell.
        This method handles the addition of a control to a cell, including the creation of the control button,
        setting its properties, and managing events related to the control addition. Due to known bugs with
        accessing controls on sheets, this method only returns the shape of the control. The shape's control
        can be accessed using ``Shape.getControl()`` if necessary.

        Returns:
            Any: The shape of the control added to the cell, or None if an error occurs or the operation is cancelled.

        Raises:
            CellDeletedError: If the cell has been deleted.

        Triggers:
            CONTROL_ADDING: Before the control is added.
            CONTROL_ADDED: After the control has been added.

        Notes:
            - Controls can lose their models when switched to a different sheet and back.
            - If the control is not found, any existing shape is removed.
            - The method logs various debug information and triggers events during the control addition process.
            - Triggers are fired using the shared_event object.
        """
        pass

    @abstractmethod
    def update_ctl_action(self) -> None:
        """
        Updates the control action for the current cell.
        This method performs the following steps:

        1. Creates a ``CancelEventArgs`` instance for the current context.
        2. Initializes a ``CellControl`` instance for the current cell.
        3. Casts the current control to ``FormCtlBase``.
        4. Creates a ``DotDict`` containing relevant data for the event.
        5. Triggers the ``CONTROL_UPDATING`` event with the created ``CancelEventArgs``.
        6. Checks if the event was cancelled and logs a debug message if so.
        7. Checks if the control is `None` and logs a debug message if so.
        8. Sets the control script using ``_set_ctl_script``.
        9. Triggers the ``CONTROL_UPDATED`` event with the updated event arguments.
        10. Logs a debug message indicating the script has been set.

        Exception Handling:
            - Logs an exception message if an error occurs while getting the current control.

        Triggers:
            CONTROL_UPDATING: Before the control is updated.
            CONTROL_UPDATED: After the control has been updated.

        Note:
            - Triggers are fired using the shared_event object
        """
        pass

    @abstractmethod
    def update_ctl(self) -> None:
        """
        Updates the control by finding the associated shape in the draw page and setting its size.
        This method performs the following steps:

        1. Logs the entry into the method.
        2. Retrieves the sheet and draw page from the calc cell.
        3. Gets the shape name from the namer.
        4. Creates a CancelEventArgs object and triggers the ``CONTROL_UPDATING`` event.
        5. If the event is cancelled, logs the cancellation and exits.
        6. Attempts to find the shape by its name in the draw page.
        7. If the shape is found, sets its size and logs the success.
        8. If the shape is not found, logs the missing shape.
        9. Triggers the ``CONTROL_UPDATED`` event.
        10. Catches and logs any exceptions that occur during the process.

        Raises:
            Exception: If any error occurs during the update process, it is logged.

        Triggers:
            CONTROL_UPDATING: Before the control is updated.
            CONTROL_UPDATED: After the control has been updated.

        Note:
            Triggers are fired using the shared_event object
        """
        pass

    @abstractmethod
    def remove_ctl(self) -> None:
        """
        Removes a control from the LibreOffice Calc sheet.
        This method performs the following steps:

        1. Logs the entry into the method.
        2. Retrieves the sheet and draw page from the calc cell.
        3. Constructs the shape name using the namer.
        4. Triggers the ``CONTROL_REMOVING`` event with relevant data.
        5. If the event is not canceled, attempts to find and remove the shape by name.
        6. Logs the success or failure of shape removal.
        7. Removes custom properties related to the control from the calc cell.
        8. Triggers the ``CONTROL_REMOVED`` event after successful removal.

        If an exception occurs during the process, it logs the error.

        Raises:
            Exception: If any error occurs during the removal process.

        Returns:
            None:

        Triggers:
            CONTROL_REMOVING: Before the control is removed.
            CONTROL_REMOVED: After the control has been inserted.

        Note:
            Triggers are fired using the shared_event object.
        """
        pass

    @property
    def ctl(self) -> CtlT:
        """Control"""
        return self.__ctl
