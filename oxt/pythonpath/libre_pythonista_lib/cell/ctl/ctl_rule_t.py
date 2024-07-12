from __future__ import annotations
from typing import Any, Protocol, Tuple
from ooodev.calc import CalcCell


class CtlRuleT(Protocol):
    """
    A class to represent a pyc formula result rule.
    """

    def __init__(self, calc_cell: CalcCell) -> None: ...

    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        ...

    def add_ctl(self) -> Any:
        """Add control to the cell"""
        ...

    def remove_ctl(self):
        """Remove control From the cell"""
        ...

    def update_ctl(self) -> None:
        """Updates the control. Usually set the controls size and pos."""
        ...

    def get_cell_pos_size(self) -> Tuple[int, int, int, int]:
        """
        Gets the position and size of the control.

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) in  ``1/100th mm``.
        """
        ...

    def update_ctl_action(self) -> None:
        """
        Updates the controls action such as setting ``actionPerformed`` macro.
        """
        ...
