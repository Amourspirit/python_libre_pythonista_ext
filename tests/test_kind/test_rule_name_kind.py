from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_rule_name_kind_str(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    else:
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind

    # Test string conversion
    assert str(RuleNameKind.CELL_DATA_TYPE_SIMPLE_CTL) == "cell_data_type_simple_ctl"
    assert str(RuleNameKind.CELL_DATA_TYPE_MP_FIGURE) == "cell_data_type_mp_figure"
    assert str(RuleNameKind.CELL_DATA_TYPE_CELL_IMG) == "cell_data_type_cell_img"
    assert str(RuleNameKind.CELL_DATA_TYPE_STR) == "cell_data_type_str"
    assert str(RuleNameKind.CELL_DATA_TYPE_NONE) == "cell_data_type_none"
    assert str(RuleNameKind.CELL_DATA_TYPE_ERROR) == "cell_data_type_error"
    assert str(RuleNameKind.CELL_DATA_TYPE_INT) == "cell_data_type_int"
    assert str(RuleNameKind.CELL_DATA_TYPE_TBL_DATA) == "cell_data_type_tbl_data"
    assert str(RuleNameKind.CELL_DATA_TYPE_FLOAT) == "cell_data_type_float"
    assert str(RuleNameKind.CELL_DATA_TYPE_PD_DF) == "cell_data_type_pd_df"
    assert str(RuleNameKind.CELL_DATA_TYPE_PD_SERIES) == "cell_data_type_pd_series"
    assert str(RuleNameKind.UNKNOWN) == "unknown"


def test_rule_name_kind_from_str(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    else:
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind

    # Test valid conversions
    assert RuleNameKind.from_str("cell_data_type_simple_ctl") == RuleNameKind.CELL_DATA_TYPE_SIMPLE_CTL
    assert RuleNameKind.from_str("cell_data_type_mp_figure") == RuleNameKind.CELL_DATA_TYPE_MP_FIGURE
    assert RuleNameKind.from_str("unknown") == RuleNameKind.UNKNOWN

    # Test invalid conversion
    assert RuleNameKind.from_str("invalid_value") == RuleNameKind.UNKNOWN


def test_rule_name_kind_from_ctl_kind(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista_lib.kind.ctl_kind import CtlKind

    # Test conversion from CtlKind
    assert RuleNameKind.from_ctl_kind(CtlKind.SIMPLE_CTL) == RuleNameKind.CELL_DATA_TYPE_SIMPLE_CTL
    assert RuleNameKind.from_ctl_kind(CtlKind.MAT_PLT_FIGURE) == RuleNameKind.CELL_DATA_TYPE_MP_FIGURE

    # Test conversion of unknown CtlKind
    class MockCtlKind:
        def __str__(self) -> str:
            return "invalid_value"

    mock_ctl = MockCtlKind()
    assert RuleNameKind.from_ctl_kind(mock_ctl) == RuleNameKind.UNKNOWN  # type: ignore


def test_rule_name_kind_values(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    else:
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind

    # Test that all enum values are defined
    expected_values = {
        "CELL_DATA_TYPE_SIMPLE_CTL": "cell_data_type_simple_ctl",
        "CELL_DATA_TYPE_MP_FIGURE": "cell_data_type_mp_figure",
        "CELL_DATA_TYPE_CELL_IMG": "cell_data_type_cell_img",
        "CELL_DATA_TYPE_STR": "cell_data_type_str",
        "CELL_DATA_TYPE_NONE": "cell_data_type_none",
        "CELL_DATA_TYPE_EMPTY": "cell_data_type_empty",
        "CELL_DATA_TYPE_ERROR": "cell_data_type_error",
        "CELL_DATA_TYPE_INT": "cell_data_type_int",
        "CELL_DATA_TYPE_TBL_DATA": "cell_data_type_tbl_data",
        "CELL_DATA_TYPE_FLOAT": "cell_data_type_float",
        "CELL_DATA_TYPE_PD_DF": "cell_data_type_pd_df",
        "CELL_DATA_TYPE_PD_SERIES": "cell_data_type_pd_series",
        "UNKNOWN": "unknown",
    }

    for name, value in expected_values.items():
        enum_member = getattr(RuleNameKind, name)
        assert enum_member.value == value
        assert str(enum_member) == value


def test_from_ctl_kind(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    for kind in CtlKind:
        result = RuleNameKind.from_ctl_kind(kind)
        assert result == RuleNameKind.from_str(str(kind))
