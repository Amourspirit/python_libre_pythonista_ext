from __future__ import annotations
import re
from ..lp_enum import LpEnum


# tested in: tests\test_doc\test_calc\test_doc\test_sheet\test_cell\test_code\test_mod_helper\test_lp_rules\test_rule_sheet_cell.py
class RuleSheetCell:
    """
    Rule to match cell only. A2 not A2:B4, not Sheet1.A2
    """

    def __init__(self, value: str) -> None:
        self._value = value

    def get_re(self) -> str:
        """Gets the regex pattern."""
        # Matches sheet cell in format: Sheet1.A2
        # ^[^.]      - start of string, first char cannot be dot
        # .*+        - followed by any chars (sheet name), possessive quantifier
        # \.        - followed by literal dot
        # [A-Za-z]{1,3} - 1-3 letters for column
        # \d{1,7}   - 1-7 digits for row
        # $         - end of string
        return r"^[^.].*\.[A-Za-z]{1,3}\d{1,7}$"

    def is_valid_sheet_name(self, sheet_name: str) -> bool:
        """
        Checks if a given string is a valid Excel sheet name.

        Args:
            sheet_name (str): The string to be validated as a sheet name.

        Returns:
            bool: True if the sheet name is valid, False otherwise.
        """

        # Rule 1: Sheet names cannot be empty or None.
        if not sheet_name:
            return False

        # Rule 2: Check for forbidden characters using a regular expression.
        # The backslash is escaped to be treated as a literal character.
        forbidden_chars_pattern = r"[:\\/?*\[\]]"
        if re.search(forbidden_chars_pattern, sheet_name):
            return False

        # Rule 3: A single quote cannot be the first or last character.
        # This check specifically looks for a single quote at the start or end of the string.
        if sheet_name.startswith("'") or sheet_name.endswith("'"):
            # This part of the rule states that a single quote inside the name is allowed.
            # The 'if' condition only checks the start and end, so it correctly implements the rule.
            return False

        # The name is valid if it passes all the checks.
        return True

    def get_is_match(self) -> bool:
        """Check if rules is a match."""

        is_match = bool(re.match(self.get_re(), self._value))
        if not is_match:
            return False
        sheet_name = self._value.rsplit(".", maxsplit=1)[0]
        return self.is_valid_sheet_name(sheet_name)

    def get_value(self) -> LpEnum:
        """Gets the value of the rule."""
        return LpEnum.SHEET_CELL

    def __repr__(self) -> str:
        return f"<RuleSheetCell({self._value})>"
