from __future__ import annotations
from typing import Any
import pandas as pd
from .rule_base import RuleBase
from ...convert_util import ConvertUtil


class RulePdTimeStampIso(RuleBase):

    def get_is_match(self, value: Any) -> bool:
        return isinstance(value, pd.Timestamp)

    def convert(self, value: Any) -> Any:
        return ConvertUtil.pandas_timestamp_to_iso8601(value)
