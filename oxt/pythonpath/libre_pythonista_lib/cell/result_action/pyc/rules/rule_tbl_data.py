from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleTblData(RuleBase):

    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_tbl_data

    def get_is_match(self) -> bool:
        obj = self.data.get("data", None)
        if obj is None:
            return False
        if not isinstance(obj, (list, tuple)):
            return False

        for item in obj:
            if not isinstance(item, (list, tuple)):
                return False

        # # Optional: Check if all inner lists or tuples have the same length
        lengths = [len(item) for item in obj]
        if lengths and lengths.count(lengths[0]) != len(lengths):
            return False

        return True

    def action(self) -> Any:
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: True,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return self.data.data
