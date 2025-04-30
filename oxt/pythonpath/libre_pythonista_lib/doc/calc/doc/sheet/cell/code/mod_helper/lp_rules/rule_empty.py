from __future__ import annotations
from ..lp_enum import LpEnum


class RuleEmpty:
    """
    Rule to match empty string.
    """

    def __init__(self, value: str) -> None:
        self._value = value

    def get_is_match(self) -> bool:
        """Check if rules is a match."""
        return self._value == ""

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.EMPTY

    def __repr__(self) -> str:
        return f"<RuleEmpty()>"
