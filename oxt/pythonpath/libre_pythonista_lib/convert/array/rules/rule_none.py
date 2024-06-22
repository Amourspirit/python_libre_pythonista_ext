from __future__ import annotations
from typing import Any
import pandas as pd
from .rule_base import RuleBase
from ...convert_util import ConvertUtil


class RuleNone(RuleBase):

    def get_is_match(self, value: Any) -> bool:
        return value is None

    def convert(self, value: Any) -> Any:
        return ""
