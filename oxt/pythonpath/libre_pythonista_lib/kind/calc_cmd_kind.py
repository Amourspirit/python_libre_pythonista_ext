from __future__ import annotations
from enum import IntEnum


class CalcCmdKind(IntEnum):
    """The kind of command"""

    SIMPLE = 1
    CELL = 2
    CELL_CACHE = 3
    SHEET = 4
    SHEET_CACHE = 5

    def __repr__(self) -> str:
        if self.name is None:
            return f"{self.__class__.__name__}.{self.value}"
        return f"{self.__class__.__name__}.{self.name}"
