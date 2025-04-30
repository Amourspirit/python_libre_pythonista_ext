from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_qry_prop_names_single(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    else:
        from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    # Mock KeyMaker
    key_maker = mocker.Mock(spec=KeyMaker)
    key_maker.ctl_state_key = "state_key"
    key_maker.ctl_shape_key = "shape_key"
    key_maker.cell_addr_key = "addr_key"
    key_maker.ctl_orig_ctl_key = "orig_key"
    key_maker.cell_array_ability_key = "array_key"
    key_maker.modify_trigger_event = "trigger_key"
    key_maker.pyc_rule_key = "rule_key"

    # Create QryPropNames instance and set mocked KeyMaker
    qry = QryPropNames(CtlPropKind.CTL_STATE)
    mocker.patch.object(qry, "_get_keys", return_value=key_maker)

    # Test single property kind
    result = qry.execute()
    assert result == {"state_key"}


def test_qry_prop_names_multiple(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    else:
        from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    # Mock KeyMaker
    key_maker = mocker.Mock(spec=KeyMaker)
    key_maker.ctl_state_key = "state_key"
    key_maker.ctl_shape_key = "shape_key"
    key_maker.cell_addr_key = "addr_key"
    key_maker.ctl_orig_ctl_key = "orig_key"
    key_maker.cell_array_ability_key = "array_key"
    key_maker.modify_trigger_event = "trigger_key"
    key_maker.pyc_rule_key = "rule_key"

    # Test multiple property kinds
    qry = QryPropNames(CtlPropKind.CTL_STATE, CtlPropKind.CTL_SHAPE, CtlPropKind.CELL_ADDR)
    mocker.patch.object(qry, "_get_keys", return_value=key_maker)

    result = qry.execute()
    assert result == {"state_key", "shape_key", "addr_key"}


def test_qry_prop_names_all(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    else:
        from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    # Mock KeyMaker
    key_maker = mocker.Mock(spec=KeyMaker)
    key_maker.ctl_state_key = "state_key"
    key_maker.ctl_shape_key = "shape_key"
    key_maker.cell_addr_key = "addr_key"
    key_maker.ctl_orig_ctl_key = "orig_key"
    key_maker.cell_array_ability_key = "array_key"
    key_maker.modify_trigger_event = "trigger_key"
    key_maker.pyc_rule_key = "rule_key"

    # Test all property kinds
    qry = QryPropNames(
        CtlPropKind.CTL_STATE,
        CtlPropKind.CTL_SHAPE,
        CtlPropKind.CELL_ADDR,
        CtlPropKind.CTL_ORIG,
        CtlPropKind.CELL_ARRAY_ABILITY,
        CtlPropKind.MODIFY_TRIGGER_EVENT,
        CtlPropKind.PYC_RULE,
    )
    mocker.patch.object(qry, "_get_keys", return_value=key_maker)

    result = qry.execute()
    assert result == {"state_key", "shape_key", "addr_key", "orig_key", "array_key", "trigger_key", "rule_key"}


def test_qry_prop_names_empty(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    else:
        from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    # Mock KeyMaker
    key_maker = mocker.Mock(spec=KeyMaker)
    key_maker.ctl_state_key = "state_key"

    # Test with no property kinds
    qry = QryPropNames()
    mocker.patch.object(qry, "_get_keys", return_value=key_maker)

    result = qry.execute()
    assert result == set()
