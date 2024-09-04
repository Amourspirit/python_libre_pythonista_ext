from __future__ import annotations
from typing import Any, Protocol


class PdRuleT(Protocol):
    """
    A class to represent a Pandas Rule.
    """

    def convert(self, value: Any) -> Any: ...
