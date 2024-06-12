from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleFloat(RuleBase):

    def get_is_match(self) -> bool:
        if self.data is None:
            return False
        return isinstance(self.data, float)

    def action(self) -> Any:
        self.cell.set_custom_property(self.cell_prop_key, "cell_data_type_float")
        return ((self.data,),)
