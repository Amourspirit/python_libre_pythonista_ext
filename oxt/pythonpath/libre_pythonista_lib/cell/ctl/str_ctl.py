from __future__ import annotations
from typing import Any, cast

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

from ooodev.units import UnitPT
from ooodev.calc import CalcCell
from ooodev.format.inner.direct.calc.alignment.text_align import HoriAlignKind
from .simple_ctl import SimpleCtl


class StrCtl(SimpleCtl):

    @override
    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_str

    @override
    def add_ctl(self) -> Any:
        shape = super().add_ctl()
        cell = cast("CalcCell", self.calc_cell)
        cell.style_align_text(hori_align=HoriAlignKind.LEFT, indent=UnitPT(14))
        return shape
