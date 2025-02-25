from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_addr(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
        from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_addr import QryAddr
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
        from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_addr import QryAddr

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        ch = CmdHandler()
        qry_handler = QryHandler()
        qry = QryAddr(cell=cell)
        assert qry_handler.handle(qry) == ""

        # Test setting new address
        cmd = CmdAddr(cell=cell, addr="sheet_index=0&cell_addr=B2")
        ch.handle(cmd)
        assert cmd.success
        assert cmd.cell == cell
        assert qry_handler.handle(qry) == "sheet_index=0&cell_addr=B2"

        # Test setting same address (should succeed but not change anything)
        cmd = CmdAddr(cell=cell, addr="sheet_index=0&cell_addr=B2")
        ch.handle(cmd)
        assert cmd.success

        # Test setting different address
        cmd = CmdAddr(cell=cell, addr="sheet_index=0&cell_addr=C3")
        ch.handle(cmd)
        assert cmd.success
        assert qry_handler.handle(qry) == "sheet_index=0&cell_addr=C3"

        # Test undo
        cmd.undo()

        # Test with Addr object instead of string
        addr = Addr("sheet_index=0&cell_addr=D4")
        cmd = CmdAddr(cell=cell, addr=addr)
        ch.handle(cmd)
        assert cmd.success
        assert qry_handler.handle(qry) == "sheet_index=0&cell_addr=D4"

        # Test with invalid address
        cmd = CmdAddr(cell=cell, addr="invalid_address")
        ch.handle(cmd)
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_addr_error_handling(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr

    cell = mocker.MagicMock()

    # Test with None address
    cmd = CmdAddr(cell=cell, addr="")
    cmd.execute()
    assert not cmd.success

    # Test execution with initialization errors
    cmd = CmdAddr(cell=cell, addr="invalid_address")
    cmd.execute()
    assert not cmd.success

    # Test undo when not successful
    cmd.undo()  # Should not raise any exceptions


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdAddr, "_get_current_state", return_value="")

    cmd = CmdAddr(cell=cell, addr="sheet_index=0&cell_addr=D4")
    assert cmd.kind == CalcCmdKind.SIMPLE

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_addr import QryAddr
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_addr import QryAddr

    # libre_pythonista_lib.query.calc.sheet.cell.qry_cell_prop_value.QryCellPropValue
    _ = mocker.patch(
        "libre_pythonista_lib.query.calc.sheet.cell.prop.qry_cell_prop_value.QryCellPropValue.execute",
        return_value=True,
    )

    cell = mocker.MagicMock()

    qry = QryAddr(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET

    assert qry.execute()
