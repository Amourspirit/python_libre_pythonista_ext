from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleStr(RuleBase):

    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_str

    def get_is_match(self) -> bool:
        result = self.data.get("data", None)
        if result is None:
            return False
        return isinstance(result, str)

    def action(self) -> Any:
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: False,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return ((self.data.data,),)
