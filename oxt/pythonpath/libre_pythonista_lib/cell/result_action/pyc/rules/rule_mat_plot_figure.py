from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleMatPlotFigure(RuleBase):

    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_mp_figure

    def get_is_match(self) -> bool:
        result = self.data.get("data", None)
        if result is None:
            return False
        data_type = self.data.get("data_type", "")
        if data_type != "file":
            return False
        details = self.data.get("details", "")
        if details != "figure":
            return False
        return True

    def action(self) -> Any:
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: False,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return (("",),)
