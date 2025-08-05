from __future__ import annotations
from typing import TYPE_CHECKING
import pytest


class TestRuleSheetNamedRange:
    """Test cases for RuleSheetNamedRange class."""

    def test_init(self, build_setup):
        """Test RuleSheetNamedRange initialization."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        rule = RuleSheetNamedRange("Sheet1.MyRange")
        assert rule._value == "Sheet1.MyRange"

    @pytest.mark.parametrize(
        "value, expected",
        [
            # Valid sheet named ranges
            ("Sheet1.MyRange", True),
            ("Sheet-1.My_Range", True),
            ("Sheet One.My_Range", True),
            ("Sheet1.My_Range_1", True),
            ("Sheet1.Range123", True),
            ("MySheet.DataRange", True),
            ("Data_Sheet.Total_Sum", True),
            ("Sheet with spaces.MyRange", True),
            ("Sheet-Name.Range_Name", True),
            ("Sheet123.A", True),  # Single letter name
            ("Sheet.MyRange123", True),
            ("Sheet.Range_With_Underscores", True),
            ("Sheet.RangeWithNumbers123", True),
            ("my_sheet_My_Range", False),
            ("my sheet.My_Range", True),
            ("my.sheet.My_Range", True),  # Multiple dots in sheet name
            # Invalid sheet named ranges - regex failures
            ("MyRange", False),  # No sheet name
            (".MyRange", False),  # Starts with dot
            ("Sheet1.", False),  # No range name
            ("Sheet1.123Range", False),  # Range name starts with number
            ("_Sheet1_Range", False),  # Range name starts with underscore
            ("Sheet1.My.Range", True),  # Multiple dots
            ("Sheet1 MyRange", False),  # No dot separator
            ("sheet1.Range!", False),  # Special character in name
            ("sheet1.Range@", False),  # Special character in name
            ("sheet1.Range#", False),  # Special character in name
            ("sheet1.Range$", False),  # Special character in name
            ("sheet1.Range%", False),  # Special character in name
            ("sheet1.Range^", False),  # Special character in name
            ("sheet1.Range&", False),  # Special character in name
            ("sheet1.Range*", False),  # Special character in name
            ("sheet1.Range(", False),  # Special character in name
            ("sheet1.Range)", False),  # Special character in name
            ("sheet1.Range+", False),  # Special character in name
            ("sheet1.Range=", False),  # Special character in name
            ("sheet1.Range[", False),  # Special character in name
            ("sheet1.Range]", False),  # Special character in name
            ("sheet1.Range{", False),  # Special character in name
            ("sheet1.Range}", False),  # Special character in name
            ("sheet1.Range|", False),  # Special character in name
            ("sheet1.Range\\", False),  # Special character in name
            ("sheet1.Range/", False),  # Special character in name
            ("sheet1.Range?", False),  # Special character in name
            ("sheet1.Range<", False),  # Special character in name
            ("sheet1.Range>", False),  # Special character in name
            ("sheet1.Range,", False),  # Special character in name
            ("sheet1.Range.", False),  # Special character in name
            ("sheet1.Range;", False),  # Special character in name
            ("sheet1.Range:", False),  # Special character in name
            ("sheet1.Range'", False),  # Special character in name
            ('sheet1.Range"', False),  # Special character in name
            # Invalid sheet named ranges - invalid sheet names (inherited from parent)
            ("Sheet:.MyRange", False),  # Invalid sheet name (colon)
            ("Sheet\\Name.MyRange", False),  # Invalid sheet name (backslash)
            ("'Sheet.MyRange", False),  # Invalid sheet name (starts with quote)
            ("Sheet'.MyRange", False),  # Invalid sheet name (ends with quote)
            ("Sheet[1].MyRange", False),  # Invalid sheet name (brackets)
            # Edge cases
            ("", False),  # Empty string
            (".", False),  # Just a dot
            ("Sheet.", False),  # Sheet name but no range name
            (".Range", False),  # Range name but no sheet name
        ],
    )
    def test_get_is_match(self, value, expected, build_setup):
        """Test complete matching logic."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        rule = RuleSheetNamedRange(value)
        assert rule.get_is_match() == expected

    def test_get_value(self, build_setup):
        """Test that get_value returns correct enum."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_enum import LpEnum
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_enum import LpEnum

        rule = RuleSheetNamedRange("Sheet1.MyRange")
        assert rule.get_value() == LpEnum.SHEET_NAMED_RNG

    def test_repr(self, build_setup):
        """Test string representation."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        rule = RuleSheetNamedRange("Sheet1.MyRange")
        assert repr(rule) == "<RuleSheetNamedRange(Sheet1.MyRange)>"

    @pytest.mark.parametrize(
        "value",
        [
            "Sheet1.MyRange",
            "Data.TotalSum",
            "Invalid.123Range",
            "",
            "NoSheet",
        ],
    )
    def test_repr_various_values(self, value, build_setup):
        """Test repr with various input values."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        rule = RuleSheetNamedRange(value)
        expected = f"<RuleSheetNamedRange({value})>"
        assert repr(rule) == expected

    def test_range_name_requirements(self, build_setup):
        """Test specific requirements for range names."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        # Range name must start with letter

        assert RuleSheetNamedRange("Sheet.A").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.Z").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.a").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.z").get_is_match() == True
        assert RuleSheetNamedRange("Sheet._").get_is_match() == True

        # Range name cannot start with number
        assert RuleSheetNamedRange("Sheet.1Range").get_is_match() == False

        # Range name can contain letters, numbers, and underscores after first character
        assert RuleSheetNamedRange("Sheet.Range123").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.Range_123").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.R_a_n_g_e_1_2_3").get_is_match() == True

    def test_case_sensitivity(self, build_setup):
        """Test case sensitivity in range names."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        assert RuleSheetNamedRange("Sheet.myrange").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.MyRange").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.MYRANGE").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.MyRaNgE").get_is_match() == True

    def test_minimum_range_name_length(self, build_setup):
        """Test minimum length requirements for range names."""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )
        else:
            from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_rules.rule_sheet_named_range import (
                RuleSheetNamedRange,
            )

        # Single character range names should be valid if they start with a letter
        assert RuleSheetNamedRange("Sheet.A").get_is_match() == True
        assert RuleSheetNamedRange("Sheet.Z").get_is_match() == True

        # But need at least one character after the dot
        assert RuleSheetNamedRange("Sheet.").get_is_match() == False


if __name__ == "__main__":
    pytest.main([__file__])
