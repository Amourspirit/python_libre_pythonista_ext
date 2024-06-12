from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleStr(RuleBase):

    def get_is_match(self) -> bool:
        if self.data is None:
            return False
        return isinstance(self.data, str)

    def action(self) -> Any:
        self.cell.set_custom_property(self.cell_prop_key, "cell_data_type_str")
        return ((self.data,),)
