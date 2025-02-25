from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_code_name(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import QryCodeName
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import QryCodeName
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        qry_handler = QryHandler()
        cmd_handler = CmdHandler()
        qry = QryCodeName(cell=cell)

        assert qry_handler.handle(qry) == ""

        # Test empty name (should fail)
        cmd = CmdCodeName(cell=cell, name="")
        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test setting new code name
        test_name = "id_test123"
        cmd = CmdCodeName(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify the code name was set
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test setting same code name (should succeed but not change anything)
        cmd = CmdCodeName(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test changing to different code name and then undoing
        new_name = "id_newtest456"
        cmd = CmdCodeName(cell=cell, name=new_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == new_name

        # Test undo
        cmd.undo()
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test deleting the code name
        cmd = CmdCodeNameDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

        # Test deleting when cell does not have property
        cmd = CmdCodeNameDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_code_name_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock an exception during execution
        mocker.patch(
            "libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set.CmdCellPropSet.execute",
            side_effect=Exception("Test exception"),
        )

        cmd = CmdCodeName(cell=cell, name="id_test_name")
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdCodeName, "_get_current_state", return_value="")

    cmd = CmdCodeName(cell=cell, name="id_test_name")
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdCodeNameDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import QryCodeName
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import QryCodeName

    cell = mocker.MagicMock()

    qry = QryCodeName(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
