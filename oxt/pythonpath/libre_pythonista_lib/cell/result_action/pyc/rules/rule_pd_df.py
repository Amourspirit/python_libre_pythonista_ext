from __future__ import annotations
from typing import Any, cast
from ooodev.calc import CalcCell
import pandas as pd
from .rule_base import RuleBase
from .....cell.state.ctl_state import CtlState
from .....cell.state.state_kind import StateKind


class RulePdDf(RuleBase):

    def __init__(self, cell: CalcCell, data: Any) -> None:
        super().__init__(cell, data)
        self.state_key = self.key_maker.ctl_state_key

    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_pd_df

    def get_is_match(self) -> bool:
        if self.data is None:
            return False
        return isinstance(self.data, pd.DataFrame)

    def _get_state(self) -> StateKind:
        state = CtlState(self.cell).get_state()
        return state

    def _set_state(self, state: StateKind) -> None:
        CtlState(self.cell).set_state(state)

    def _pandas_to_array(self) -> Any:
        df = cast(pd.DataFrame, self.data)
        data_tuple = tuple(df.itertuples(index=False, name=None))
        return data_tuple

    def action(self) -> Any:
        state = self._get_state()
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: True,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
                self.state_key: state,
            }
        )
        if state == StateKind.ARRAY:
            return self._pandas_to_array()
        return (("",),)
