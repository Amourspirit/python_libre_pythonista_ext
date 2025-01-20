from __future__ import annotations
from typing import Any, TYPE_CHECKING

from .rule_base import RuleBase
from .....cell.state.ctl_state import CtlState
from .....cell.state.state_kind import StateKind


if TYPE_CHECKING:
    from .......___lo_pip___.debug.break_mgr import BreakMgr, check_breakpoint
else:
    from ___lo_pip___.debug.break_mgr import BreakMgr, check_breakpoint

break_mgr = BreakMgr()
# break_mgr.add_breakpoint("libre_pythonista_lib.cell.result_action.pyc.rules.rule_tbl_data.action")


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
        return not (lengths and lengths.count(lengths[0]) != len(lengths))

    def _get_state(self) -> StateKind:
        state = CtlState(self.cell).get_state()
        return state

    @check_breakpoint("libre_pythonista_lib.cell.result_action.pyc.rules.rule_tbl_data.action")
    def action(self) -> Any:  # noqa: ANN401
        state = self._get_state()
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: True,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        if state == StateKind.ARRAY:
            return self.data.data
        return (("",),)
