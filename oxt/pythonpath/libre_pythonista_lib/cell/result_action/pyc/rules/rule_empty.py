from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from .rule_base import RuleBase
from .....utils import str_util

if TYPE_CHECKING:
    from .....code.py_source_mgr import PySource


class RuleEmpty(RuleBase):
    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_empty

    def get_is_match(self) -> bool:
        result = cast("PySource", self.data.get("py_src", None))
        if result is None:
            return False
        code = str_util.clean_string(result.source_code)
        return code == ""

    def action(self) -> Any:  # noqa: ANN401
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: False,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return ((None,),)
