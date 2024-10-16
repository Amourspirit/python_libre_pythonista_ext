from __future__ import annotations
from typing import Any

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

try:
    import pandas as pd
except ImportError:
    pd = None

from .rule_base import RuleBase
from ...convert_util import ConvertUtil


class RulePdTimeCalcNumDate(RuleBase):

    @override
    def get_is_match(self, value: Any) -> bool:
        if pd is None:
            return False
        return isinstance(value, pd.Timestamp)

    @override
    def convert(self, value: Any) -> Any:
        return ConvertUtil.lo_date_to_pandas_timestamp(value)
