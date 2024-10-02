from __future__ import annotations
import re
from ..lp_enum import LpEnum


class RuleSheetCell:
    """
    Rule to match cell only. A2 not A2:B4, not Sheet1.A2
    """

    def __init__(self, value: str) -> None:
        self._value = value
        self._re = r"^[A-Za-z\s\d]+\.[A-Za-z]{1,3}\d{1,7}$"

    def get_is_match(self) -> bool:
        """Check if rules is a match."""

        return bool(re.match(self._re, self._value))

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.SHEET_CELL

    def __repr__(self) -> str:
        return f"<RuleSheetCell({self._value})>"
