from __future__ import annotations
from typing import Any

from .simple_ctl import SimpleCtl


class FloatCtl(SimpleCtl):

    def add_ctl(self) -> Any:
        btn = super().add_ctl()
        return btn
