from __future__ import annotations
from typing import Protocol
from ..lp_enum import LpEnum


class LpRuleT(Protocol):
    """
    A class to represent a code rule.
    """

    def __init__(self, value: str) -> None: ...

    def get_is_match(self) -> bool:
        """Check if rules is a match."""
        ...

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        ...
