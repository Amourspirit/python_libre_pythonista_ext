from __future__ import annotations
import contextlib
from ooodev.calc import CalcCell
from .state_base import StateBase
from .state_kind import StateKind
from ...const import UNO_DISPATCH_DF_STATE, UNO_DISPATCH_DS_STATE


class CtlState(StateBase):
    """Class for managing the state of a DataSeries in a Calc cell."""

    def __init__(self, cell: CalcCell) -> None:
        """
        Constructor

        Args:
            cell (CalcCell): The cell to manage the state of.
        """
        super().__init__(cell)

    def get_state(self) -> StateKind:
        """
        Gets the state

        Returns:
            StateKind: The state.
        """
        if self.cell.has_custom_property(self.key_maker.ctl_state_key):
            state = self.cell.get_custom_property(self.key_maker.ctl_state_key, StateKind.PY_OBJ.value)
            with contextlib.suppress(Exception):
                return StateKind(state)

        return StateKind.PY_OBJ

    def set_state(self, value: StateKind) -> None:
        """
        Sets the state.

        If the state is ``StateKind.UNKNOWN``, the custom property is removed.

        Args:
            value (StateKind): The state.
        """
        if value == StateKind.UNKNOWN:
            if self.cell.has_custom_property(self.key_maker.ctl_state_key):
                self.cell.remove_custom_property(self.key_maker.ctl_state_key)
            return
        self.cell.set_custom_property(self.key_maker.ctl_state_key, int(value))
