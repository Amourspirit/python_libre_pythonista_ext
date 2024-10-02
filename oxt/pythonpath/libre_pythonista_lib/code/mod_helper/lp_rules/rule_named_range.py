from __future__ import annotations
import re
from ..lp_enum import LpEnum


class RuleNamedRange:
    """
    Rule to match named range such as myrange or My_Range_1
    """

    def __init__(self, value: str) -> None:
        self._value = value
        self._re = r"^[A-Za-z][A-Za-z0-9_]+$"

    def get_is_match(self) -> bool:
        """Check if rules is a match."""

        return bool(re.match(self._re, self._value))

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.NAMED_RNG

    def __repr__(self) -> str:
        return f"<RuleNamedRange({self._value})>"
