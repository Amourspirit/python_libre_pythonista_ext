from __future__ import annotations
from typing import Any

from .rule_base import RuleBase
from ....errors.general_error import GeneralError


class RuleError(RuleBase):
    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_error

    def get_is_match(self) -> bool:
        result = self.data.get("data", None)
        return isinstance(result, GeneralError)

    def action(self) -> Any:  # noqa: ANN401
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: False,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return ((None,),)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.cell.cell_obj}, ERROR)>"
