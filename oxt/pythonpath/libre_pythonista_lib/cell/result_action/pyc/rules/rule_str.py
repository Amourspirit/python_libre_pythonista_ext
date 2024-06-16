from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleStr(RuleBase):

    def _get_data_type_name(self) -> str:
        return "cell_data_type_str"

    def get_is_match(self) -> bool:
        if self.data is None:
            return False
        return isinstance(self.data, str)

    def action(self) -> Any:
        self._update_properties(
            **{self.cell_prop_key: self.data_type_name, self.cell_pyc_rule_key: self.data_type_name}
        )
        return ((self.data,),)
