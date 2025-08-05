from __future__ import annotations
import re
from .rule_sheet_cell import RuleSheetCell
from ..lp_enum import LpEnum

# tested in: tests\test_doc\test_calc\test_doc\test_sheet\test_cell\test_code\test_mod_helper\test_lp_rules\test_rule_sheet_cell.py


class RuleSheetRange(RuleSheetCell):
    """
    Rule to match sheet range only. Sheet1.A2:B4
    """

    def __init__(self, value: str) -> None:
        self._value = value

    def get_re(self) -> str:
        """Gets the regex pattern."""
        # Matches sheet range in format: Sheet1.A2:B4
        # ^[^.]      - start of string, first char cannot be dot
        # .*+        - followed by any chars (sheet name), possessive quantifier
        # \.        - followed by literal dot
        # [A-Za-z]{1,3} - 1-3 letters for column
        # \d{1,7}   - 1-7 digits for row
        # :         - literal colon
        # [A-Za-z]{1,3} - 1-3 letters for second column
        # \d{1,7}   - 1-7 digits for second row
        # $         - end of string
        return r"^[^.].*\.[A-Za-z]{1,3}\d{1,7}:[A-Za-z]{1,3}\d{1,7}$"

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.SHEET_RNG

    def __repr__(self) -> str:
        return f"<RuleSheetRange({self._value})>"
