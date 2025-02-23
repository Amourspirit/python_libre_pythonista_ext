from __future__ import annotations
from ooodev.utils.helper.dot_dict import DotDict


class Ctl(DotDict):
    def __init__(self) -> None:
        DotDict.__init__(self, missing_attr_val=None)
