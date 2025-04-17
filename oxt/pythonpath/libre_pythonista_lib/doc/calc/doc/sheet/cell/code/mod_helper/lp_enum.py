from __future__ import annotations

from enum import Enum


class LpEnum(Enum):
    NONE = 0
    EMPTY = 1
    CELL_ONLY = 2
    SHEET_CELL = 3
    RNG_ONLY = 4
    SHEET_RNG = 5
    NAMED_RNG = 6
    SHEET_NAMED_RNG = 7
