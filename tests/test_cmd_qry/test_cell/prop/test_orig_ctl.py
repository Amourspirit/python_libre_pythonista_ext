from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_orig_ctl(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl import CmdOrigCtl
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_orig_ctl import QryOrigCtl
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl_del import CmdOrigCtlDel
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl import CmdOrigCtl
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_orig_ctl import QryOrigCtl
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl_del import CmdOrigCtlDel
        from libre_pythonista_lib.utils.result import Result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()
        qry = QryOrigCtl(cell=cell)

        # Test empty name (should fail)
        cmd = CmdOrigCtl(cell=cell, name="")
        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test setting new control name
        test_name = "cell_data_type_str"
        cmd = CmdOrigCtl(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify the control name was set
        result = qry_handler.handle(qry)
        assert Result.is_success(result)
        assert result.data == test_name

        # Test setting same control name (should succeed but not change anything)
        cmd = CmdOrigCtl(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert Result.is_success(result)
        assert result.data == test_name

        # Test changing to different control name and then undoing
        new_name = "cell_data_type_int"
        cmd = CmdOrigCtl(cell=cell, name=new_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert Result.is_success(result)
        assert result.data == new_name

        # Test undo
        cmd.undo()
        result = qry_handler.handle(qry)
        assert Result.is_success(result)
        assert result.data == test_name

        # Test deleting the code name
        cmd = CmdOrigCtlDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert Result.is_failure(result)

        # Test deleting when cell does not have property
        cmd = CmdOrigCtlDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert Result.is_failure(result)

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_orig_ctl_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl import CmdOrigCtl
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl import CmdOrigCtl

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

        cmd = CmdOrigCtl(cell=cell, name="cell_data_type_str")
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl import CmdOrigCtl
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl import CmdOrigCtl
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdOrigCtl, "_get_current_state", return_value="")

    cmd = CmdOrigCtl(cell=cell, name="cell_data_type_str")
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl_del import CmdOrigCtlDel
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_orig_ctl_del import CmdOrigCtlDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdOrigCtlDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_orig_ctl import QryOrigCtl
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_orig_ctl import QryOrigCtl

    cell = mocker.MagicMock()

    qry = QryOrigCtl(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
