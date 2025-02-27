from __future__ import annotations
from enum import IntEnum


class CalcQryKind(IntEnum):
    """The kind of query"""

    SIMPLE = 1
    SIMPLE_CACHE = 2
    CELL = 3
    CELL_CACHE = 4
    SHEET = 5
    SHEET_CACHE = 6

    def __repr__(self) -> str:
        if self.name is None:
            return f"{self.__class__.__name__}.{self.value}"
        return f"{self.__class__.__name__}.{self.name}"
