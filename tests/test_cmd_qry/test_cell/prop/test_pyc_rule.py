from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_pyc_rule(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule_del import CmdPycRuleDel
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule_del import CmdPycRuleDel

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()
        qry = QryPycRule(cell=cell)

        # Test empty name (should fail)
        cmd = CmdPycRule(cell=cell, name="")
        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test setting new pyc rule
        test_name = "cell_data_type_str"
        cmd = CmdPycRule(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify the pyc rule was set
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test setting same pyc rule (should succeed but not change anything)
        cmd = CmdPycRule(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test changing to different pyc rule and then undoing
        new_name = "cell_data_type_int"
        cmd = CmdPycRule(cell=cell, name=new_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == new_name

        # Test undo
        cmd.undo()
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test deleting the code name
        cmd = CmdPycRuleDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

        # Test deleting when cell does not have property
        cmd = CmdPycRuleDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_pyc_rule_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock execute to raise an exception
        mocker.patch(
            "libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set.CmdCellPropSet.execute",
            side_effect=Exception("Test exception"),
        )

        cmd = CmdPycRule(cell=cell, name="cell_data_type_str")
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdPycRule, "_get_current_state", return_value="")

    cmd = CmdPycRule(cell=cell, name="cell_data_type_str")
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule_del import CmdPycRuleDel
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule_del import CmdPycRuleDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdPycRuleDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule

    cell = mocker.MagicMock()

    qry = QryPycRule(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
