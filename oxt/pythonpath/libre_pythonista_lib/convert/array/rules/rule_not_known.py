from __future__ import annotations
from typing import Any
import pandas as pd
from .rule_base import RuleBase
from ...convert_util import ConvertUtil


class RuleNotKnown(RuleBase):

    def get_is_match(self, value: Any) -> bool:
        return not isinstance(value, (float, int, str, bool))

    def convert(self, value: Any) -> Any:
        return str(value)
