from __future__ import annotations
from typing import Any, Protocol
from ooodev.calc import CalcCell


class PycRuleT(Protocol):
    """
    A class to represent a pyc formula result rule.
    """

    def __init__(self, cell: CalcCell, data: Any) -> None: ...

    def get_is_match(self) -> bool:
        """Gets if data is a Match for the current rule."""
        ...

    def action(self) -> Any:
        """Action to be taken when the rule is matched. Should return a value that can be used by the pyc function."""
        ...
