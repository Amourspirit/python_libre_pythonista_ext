from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_code_name(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        qry_handler = QryHandlerFactory.get_qry_handler()
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry = QryCodeName(cell=cell)

        assert qry_handler.handle(qry) == ""

        cmd = CmdCodeName(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify the code name was set
        code_id = qry_handler.handle(qry)
        assert code_id

        # Test undo
        cmd_handler.undo()
        result = qry_handler.handle(qry)
        assert result == ""

        # Test redo
        cmd_handler.redo()
        result = qry_handler.handle(qry)
        assert result == code_id

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
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock an exception during execution
        mocker.patch(
            "libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set.CmdCellPropSet.execute",
            side_effect=Exception("Test exception"),
        )

        cmd = CmdCodeName(cell=cell)
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdCodeName(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdCodeNameDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName

    cell = mocker.MagicMock()

    qry = QryCodeName(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
