from __future__ import annotations
from typing import Any
from ooodev.utils.helper.dot_dict import DotDict


class Ctl(DotDict[Any]):
    def __init__(self) -> None:
        DotDict.__init__(self, missing_attr_val=None)
