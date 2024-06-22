from __future__ import annotations
from typing import Any
import pandas as pd
from .rule_base import RuleBase
from ...convert_util import ConvertUtil


class RulePdToIsoDate(RuleBase):

    def convert(self, value: pd.DataFrame) -> Any:
        cols = self.get_all_date_columns(value)
        return self._convert_pandas_lo_date_columns(value, *cols)

    def _convert_pandas_lo_date_columns(self, df: pd.DataFrame, *columns: str | int) -> pd.DataFrame:
        """
        Converts date columns to Pandas Timestamp.

        Note:
            Does not make a copy of the DataFrame.
        """
        for col in columns:
            if isinstance(col, int):
                col_name = df.columns[col]
                # df.iloc[:, col] = df.iloc[:, col].apply(cls.libreoffice_date_to_pandas)
            else:
                col_name = col
            df[col_name] = df[col_name].apply(ConvertUtil.pandas_timestamp_to_iso8601)
        return df
