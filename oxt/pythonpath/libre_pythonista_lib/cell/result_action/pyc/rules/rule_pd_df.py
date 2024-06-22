from __future__ import annotations
from typing import Any, cast
from ooodev.calc import CalcCell
import pandas as pd
from .rule_base import RuleBase
from .....cell.state.ctl_state import CtlState
from .....cell.state.state_kind import StateKind
from .....const import UNO_DISPATCH_DF_STATE
from .....utils.pandas_util import PandasUtil


class RulePdDf(RuleBase):

    def __init__(self, cell: CalcCell, data: Any) -> None:
        super().__init__(cell, data)
        self.state_key = self.key_maker.ctl_state_key

    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_pd_df

    def get_dispatch_state(self) -> str:
        """
        Gets the dispatch command from the const ``UNO_DISPATCH_DF_STATE``.
        """
        return UNO_DISPATCH_DF_STATE

    def get_is_match(self) -> bool:
        result = self.data.get("data", None)
        if result is None:
            return False
        is_df = isinstance(result, pd.DataFrame)
        if not is_df:
            return False
        headers = self.data.get("headers", False)
        if headers:
            return False
        return True

    def _get_state(self) -> StateKind:
        state = CtlState(self.cell).get_state()
        return state

    def _set_state(self, state: StateKind) -> None:
        CtlState(self.cell).set_state(state)

    def _pandas_to_array(self) -> Any:
        df = cast(pd.DataFrame, self.data.data)
        return PandasUtil.pandas_to_array(df)
        has_headers = PandasUtil.has_headers(df)
        if not has_headers:
            df.values.tolist()

        # data_tuple = tuple(df.itertuples(index=False, name=None))
        # return data_tuple
        headers = [df.columns.tolist()]
        # Append the DataFrame values to the list
        list_values = df.values.tolist()
        if not list_values:
            return headers

        has_index_names = PandasUtil.has_index_names(df)
        if has_index_names:
            index_names = PandasUtil.get_index_names(df)
            # insert an index name into each row
            for i, index_name in enumerate(index_names):
                list_values[i].insert(0, index_name)
            # insert an empty value into the start of the headers
            headers[0].insert(0, "")

        result = headers + list_values
        return result

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

    def __repr__(self) -> str:
        return f"<RulePdDf({self.cell.cell_obj}, {type(self.data).__name__})>"
