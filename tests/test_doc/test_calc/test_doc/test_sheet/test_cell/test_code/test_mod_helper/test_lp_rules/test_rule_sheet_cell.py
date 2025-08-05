from __future__ import annotations
from typing import TYPE_CHECKING
import pytest


class TestRuleSheetCell:
    """Test cases for RuleSheetCell class."""

    def test_init(self, build_setup):
        """Test RuleSheetCell initialization."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        rule = RuleSheetCell("Sheet1.A1")
        assert rule._value == "Sheet1.A1"

    def test_get_re(self, build_setup):
        """Test regex pattern generation."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )

        rule = RuleSheetCell("Sheet1.A1")
        pattern = rule.get_re()
        expected = r"^[^.].*\.[A-Za-z]{1,3}\d{1,7}$"
        assert pattern == expected

    @pytest.mark.parametrize(
        "sheet_name, expected",
        [
            # Valid sheet names
            ("Sheet1", True),
            ("MySheet", True),
            ("Data_2023", True),
            ("Sheet with spaces", True),
            ("Sheet-Name", True),
            ("Sheet123", True),
            ("A", True),
            ("Sheet'Name", True),  # Single quote in middle is allowed
            # Invalid sheet names
            ("", False),  # Empty string
            ("Sheet:", False),  # Contains colon
            ("Sheet\\", False),  # Contains backslash
            ("Sheet/", False),  # Contains forward slash
            ("Sheet?", False),  # Contains question mark
            ("Sheet*", False),  # Contains asterisk
            ("Sheet[", False),  # Contains opening bracket
            ("Sheet]", False),  # Contains closing bracket
            ("'Sheet", False),  # Starts with single quote
            ("Sheet'", False),  # Ends with single quote
            ("'Sheet'", False),  # Both starts and ends with single quote
        ],
    )
    def test_is_valid_sheet_name(self, sheet_name, expected, build_setup):
        """Test sheet name validation."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )

        rule = RuleSheetCell("dummy")
        assert rule.is_valid_sheet_name(sheet_name) == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            # Valid sheet cell references
            ("Sheet1.A1", True),
            ("MySheet.B2", True),
            ("Data.Z99", True),
            ("Sheet123.AA100", True),
            ("ValidName.ABC1234567", True),  # Max column letters and row digits
            ("Sheet_Name.A1", True),
            ("Sheet-Name.B2", True),
            ("Sheet with spaces.C3", True),
            # Invalid sheet cell references - regex failures
            ("A1", False),  # No sheet name
            (".A1", False),  # Starts with dot
            ("Sheet1.", False),  # No cell reference
            ("Sheet1.A", False),  # No row number
            ("Sheet1.1", False),  # No column letters
            ("Sheet1.AAAA1", False),  # Too many column letters (4)
            ("Sheet1.A12345678", False),  # Too many row digits (8)
            ("Sheet1.A1.B2", True),  # Multiple dots
            ("Sheet1 A1", False),  # No dot separator
            # Invalid sheet cell references - invalid sheet names
            ("Sheet:.A1", False),  # Invalid sheet name (colon)
            ("Sheet\\Name.A1", False),  # Invalid sheet name (backslash)
            ("'Sheet.A1", False),  # Invalid sheet name (starts with quote)
            ("Sheet'.A1", False),  # Invalid sheet name (ends with quote)
            ("Sheet[1].A1", False),  # Invalid sheet name (brackets)
        ],
    )
    def test_get_is_match(self, value, expected, build_setup):
        """Test complete matching logic."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )

        rule = RuleSheetCell(value)
        assert rule.get_is_match() == expected

    def test_get_value(self, build_setup):
        """Test that get_value returns correct enum."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )

            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_enum import LpEnum
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_enum import LpEnum
        rule = RuleSheetCell("Sheet1.A1")
        assert rule.get_value() == LpEnum.SHEET_CELL

    def test_repr(self, build_setup):
        """Test string representation."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        rule = RuleSheetCell("Sheet1.A1")
        assert repr(rule) == "<RuleSheetCell(Sheet1.A1)>"

    @pytest.mark.parametrize(
        "value",
        [
            "Sheet1.A1",
            "MyData.Z999",
            "Invalid.Reference",
            "",
            "NoSheet",
        ],
    )
    def test_repr_various_values(self, value, build_setup):
        """Test repr with various input values."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        rule = RuleSheetCell(value)
        expected = f"<RuleSheetCell({value})>"
        assert repr(rule) == expected

    def test_edge_cases_column_letters(self, build_setup):
        """Test edge cases for column letter validation."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        # Test minimum and maximum valid column letters
        assert RuleSheetCell("Sheet.A1").get_is_match() == True  # 1 letter
        assert RuleSheetCell("Sheet.AB1").get_is_match() == True  # 2 letters
        assert RuleSheetCell("Sheet.ABC1").get_is_match() == True  # 3 letters
        assert RuleSheetCell("Sheet.ABCD1").get_is_match() == False  # 4 letters (invalid)

    def test_edge_cases_row_numbers(self, build_setup):
        """Test edge cases for row number validation."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        # Test minimum and maximum valid row numbers
        assert RuleSheetCell("Sheet.A1").get_is_match() == True  # 1 digit
        assert RuleSheetCell("Sheet.A1234567").get_is_match() == True  # 7 digits
        assert RuleSheetCell("Sheet.A12345678").get_is_match() == False  # 8 digits (invalid)

    def test_case_sensitivity(self, build_setup):
        """Test case sensitivity in column letters."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_cell import (
                RuleSheetCell,
            )
        assert RuleSheetCell("Sheet.a1").get_is_match() == True  # lowercase
        assert RuleSheetCell("Sheet.A1").get_is_match() == True  # uppercase
        assert RuleSheetCell("Sheet.aB1").get_is_match() == True  # mixed case


if __name__ == "__main__":
    pytest.main([__file__])
