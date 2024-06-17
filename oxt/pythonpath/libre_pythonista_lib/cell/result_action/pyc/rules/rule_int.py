from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleInt(RuleBase):

    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_int

    def get_is_match(self) -> bool:
        if self.data is None:
            return False
        return isinstance(self.data, int)

    def action(self) -> Any:
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: False,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return ((self.data,),)
