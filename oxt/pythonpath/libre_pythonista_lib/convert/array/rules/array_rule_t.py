from __future__ import annotations
from typing import Any, Protocol


class ArrayRuleT(Protocol):
    """
    A class to represent a Array Rule.
    """

    def get_is_match(self, value: Any) -> bool: ...

    def convert(self, value: Any) -> Any: ...
