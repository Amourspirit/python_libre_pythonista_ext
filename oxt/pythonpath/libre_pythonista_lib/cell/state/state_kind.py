from __future__ import annotations
from enum import IntEnum


class StateKind(IntEnum):
    UNKNOWN = 0
    PY_OBJ = 1
    ARRAY = 2
