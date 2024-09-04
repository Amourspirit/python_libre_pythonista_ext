from __future__ import annotations
from typing import Protocol
from typing import Any, List, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.utils.data_type.range_obj import RangeObj


from ...code.py_source_mgr import PySource
from ...cell.state.ctl_state import CtlState


if TYPE_CHECKING:
    from ooodev.proto.event_observer import EventObserver
    from ooodev.utils.type_var import EventCallback
    from ooodev.events.args.event_args_t import EventArgsT
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class ArrayT(Protocol):
    """
    A class to represent a code rule.
    """

    def get_data(self) -> PySource:
        """
        Gets the data as a DotDict for a PySource instance.

        Returns:
            DotDict: Data as a DotDict
        """
        ...

    def get_rows_cols(self) -> List[int]:
        """
        Gets the number of rows and columns for a DataFrame.

        Returns:
            List[int]: Number of rows and columns
        """
        raise NotImplementedError

    def get_formula(self) -> str:
        """Gets the formula for the cell. any ``{`` and ``}`` are removed."""
        ...

    def set_formula_array(self, **kwargs: Any) -> None:
        """
        Set the formula for the cell as an array formula.

        Other Args:
            **kwargs: Additional arguments that are passed to the event data.

        Raises:
            CellFormulaExpandError: If the range can not expand into the needed range.

        Note:
            Setting the formula array for the cell here will not update the cell control if there is one.
        """
        ...

    def set_formula(self, **kwargs: Any) -> None:
        """
        Sets the formula for the cell.

        Other Args:
            **kwargs: Additional arguments that are passed to the event data.

        Note:
            Setting the formula for the cell here will not update the cell control if there is one.
        """
        ...

    def get_formula_range(self) -> RangeObj:
        """
        Gets the range of the formula.
        This is the range of the formula in the cell and may not match the actual data range
        if the data has changed.

        Returns:
            RangeObj: The range of the formula.
        """
        ...

    def update_required(self) -> bool:
        """
        Checks if the cell needs an update.

        If the cell is not an array formula, then an update is not needed.
        If the cell is not expanded as a array formula, then an update is not needed.
        If the cell is an array formula, then an update is needed if the data range has changed.

        Returns:
            bool: True if the cell needs an update.
        """
        ...

    def update(self) -> None:
        """
        Updates the cell if needed.

        Calls ``update_required()`` to check if an update is needed.
        """
        ...

    # region Properties
    @property
    def ctl_state(self) -> CtlState:
        """Gets the control state."""
        ...

    @property
    def cell(self) -> CalcCell:
        """Gets the cell."""
        ...

    @property
    def log(self) -> OxtLogger:
        """Gets the logger."""
        ...

    # endregion Properties

    # region Events
    def add_event_observers(self, *args: EventObserver) -> None:
        """
        Adds observers that gets their ``trigger`` method called when this class ``trigger`` method is called.

        Parameters:
            args (EventObserver): One or more observers to add.

        Returns:
            None:

        Note:
            Observers are removed automatically when they are out of scope.
        """
        ...

    def remove_event_observer(self, observer: EventObserver) -> bool:
        """
        Removes an observer

        Args:
            observer (EventObserver): One or more observers to add.

        Returns:
            bool: ``True`` if observer has been removed; Otherwise, ``False``.
        """
        ...

    def subscribe_event(self, event_name: str, callback: EventCallback) -> None:
        """
        Add an event listener to current instance.

        Args:
            event_name (str): Event Name.
            callback (EventCallback): Callback of the event listener.

        Returns:
            None:
        """
        ...

    def unsubscribe_event(self, event_name: str, callback: EventCallback) -> None:
        """
        Remove an event listener from current instance.

        Args:
            event_name (str): Event Name.
            callback (EventCallback): Callback of the event listener.

        Returns:
            None:
        """
        ...

    def trigger_event(self, event_name: str, event_args: EventArgsT):
        """
        Trigger an event on current instance.

        Args:
            event_name (str): Event Name.
            event_args (EventArgsT): Event Args.

        Returns:
            None:
        """
        ...

    # endregion Events

    @property
    def event_observer(self) -> EventObserver:
        """Gets/Sets The Event Observer for this instance."""
        ...

    @event_observer.setter
    def event_observer(self, value: EventObserver) -> None:
        """Sets The Event Observer for this instance."""
        ...

    # endregion Events
