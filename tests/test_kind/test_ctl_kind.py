from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_ctl_kind_values(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
    # Test enum values
    assert int(CtlKind.UNKNOWN) == 0
    assert int(CtlKind.ERROR) == 1
    assert int(CtlKind.NONE) == 2
    assert int(CtlKind.EMPTY) == 3
    assert int(CtlKind.SIMPLE_CTL) == 4
    assert int(CtlKind.STRING) == 5
    assert int(CtlKind.FLOAT) == 6
    assert int(CtlKind.INTEGER) == 7
    assert int(CtlKind.DATA_FRAME) == 8
    assert int(CtlKind.SERIES) == 9
    assert int(CtlKind.DATA_TABLE) == 10
    assert int(CtlKind.IMAGE) == 11
    assert int(CtlKind.MAT_PLT_FIGURE) == 12


def test_ctl_kind_str(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
    # Test string representation
    assert str(CtlKind.UNKNOWN) == "unknown"
    assert str(CtlKind.ERROR) == "cell_data_type_error"
    assert str(CtlKind.NONE) == "cell_data_type_none"
    assert str(CtlKind.EMPTY) == "cell_data_type_empty"
    assert str(CtlKind.SIMPLE_CTL) == "cell_data_type_simple_ctl"
    assert str(CtlKind.STRING) == "cell_data_type_str"
    assert str(CtlKind.FLOAT) == "cell_data_type_float"
    assert str(CtlKind.INTEGER) == "cell_data_type_int"
    assert str(CtlKind.DATA_FRAME) == "cell_data_type_pd_df"
    assert str(CtlKind.SERIES) == "cell_data_type_pd_series"
    assert str(CtlKind.DATA_TABLE) == "cell_data_type_tbl_data"
    assert str(CtlKind.IMAGE) == "cell_data_type_cell_img"
    assert str(CtlKind.MAT_PLT_FIGURE) == "cell_data_type_mp_figure"


def test_from_strbuild_setup(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
    # Test from_str method
    assert CtlKind.from_str("unknown") == CtlKind.UNKNOWN
    assert CtlKind.from_str("cell_data_type_error") == CtlKind.ERROR
    assert CtlKind.from_str("cell_data_type_none") == CtlKind.NONE
    assert CtlKind.from_str("cell_data_type_empty") == CtlKind.EMPTY

    # Test invalid string
    assert CtlKind.from_str("invalid_kind") == CtlKind.UNKNOWN


def test_from_rule_name_kind(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    for kind in RuleNameKind:
        result = CtlKind.from_rule_name_kind(kind)
        assert result == CtlKind.from_str(str(kind))
