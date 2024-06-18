from __future__ import annotations
from typing import Any, Protocol
from ooodev.calc import CalcCell


class CtlRuleT(Protocol):
    """
    A class to represent a pyc formula result rule.
    """

    def __init__(self, cell: CalcCell) -> None: ...

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
        ...