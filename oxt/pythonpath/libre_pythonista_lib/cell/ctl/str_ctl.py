from __future__ import annotations
from typing import Any, cast

from ooodev.units import UnitPT
from ooodev.calc import CalcCell
from ooodev.format.inner.direct.calc.alignment.text_align import HoriAlignKind
from .simple_ctl import SimpleCtl


class StrCtl(SimpleCtl):

    def add_ctl(self) -> Any:
        shape = super().add_ctl()
        cell = cast("CalcCell", self.calc_cell)
        cell.style_align_text(hori_align=HoriAlignKind.LEFT, indent=UnitPT(14))
        return shape
