from __future__ import annotations
import re
from .rule_sheet_cell import RuleSheetCell
from ..lp_enum import LpEnum


# tested in: tests\test_doc\test_calc\test_doc\test_sheet\test_cell\test_code\test_mod_helper\test_lp_rules\test_rule_sheet_named_range.py
class RuleSheetNamedRange(RuleSheetCell):
    """
    Rule to match Sheet Named Range such as Sheet1.MyRange or Sheet1.My_Range_1
    """

    def __init__(self, value: str) -> None:
        self._value = value

    def get_re(self) -> str:
        """Gets the regex pattern."""
        # Matches sheet named range in format: Sheet1.MyRange or my.sheet.My_Range
        # ^[^.]      - start of string, first char cannot be dot
        # .*         - followed by any chars (sheet name)
        # \.        - followed by literal dot
        # [A-Za-z]   - first char after dot must be letter
        # [A-Za-z0-9_]+ - followed by letters, numbers or underscores
        # $         - end of string
        return r"^[^.].*\.[A-Za-z_][A-Za-z0-9_]*$"

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.SHEET_NAMED_RNG

    def __repr__(self) -> str:
        return f"<RuleSheetNamedRange({self._value})>"
