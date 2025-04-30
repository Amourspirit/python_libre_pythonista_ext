from __future__ import annotations
import re
from ..lp_enum import LpEnum


class RuleSheetNamedRange:
    """
    Rule to match Sheet Named Range such as Sheet1.MyRange or Sheet1.My_Range_1
    """

    def __init__(self, value: str) -> None:
        self._value = value
        self._re = r"^[A-Za-z\s\d]+\.[A-Za-z][A-Za-z0-9_]+$"

    def get_is_match(self) -> bool:
        """Check if rules is a match."""

        return bool(re.match(self._re, self._value))

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.SHEET_NAMED_RNG

    def __repr__(self) -> str:
        return f"<RuleSheetNamedRange({self._value})>"
