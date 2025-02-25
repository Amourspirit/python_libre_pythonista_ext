from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_state(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state import CmdState
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cell.state.state_kind import StateKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_state import QryState
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state_del import CmdStateDel
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state import CmdState
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cell.state.state_kind import StateKind
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_state import QryState
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state_del import CmdStateDel

    # _ = mocker.patch("libre_pythonista_lib.cmd.calc.sheet.cell.cmd_state.LogInst")

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()
        qry = QryState(cell=cell)

        # Test setting new state
        cmd = CmdState(cell=cell, state=StateKind.UNKNOWN)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert cmd.cell == cell
        assert qry_handler.handle(qry) == StateKind.UNKNOWN

        # Test setting same state (should succeed but not change anything)
        cmd = CmdState(cell=cell, state=StateKind.PY_OBJ)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert qry_handler.handle(qry) == StateKind.PY_OBJ

        # Test changing to different state
        cmd = CmdState(cell=cell, state=StateKind.ARRAY)
        cmd_handler.handle(cmd)
        assert cmd.success

        assert qry_handler.handle(qry) == StateKind.ARRAY

        # Test undo
        cmd.undo()
        assert cmd.success

        assert qry_handler.handle(qry) == StateKind.PY_OBJ

        # Test failed execution
        cmd = CmdState(cell=cell, state=StateKind.ARRAY)
        mocker.patch.object(cmd, "_get_state", side_effect=AttributeError("Simulated error"))

        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test deleting the code name
        cmd = CmdStateDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == StateKind.UNKNOWN

        # Test deleting when cell does not have property
        cmd = CmdStateDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == StateKind.UNKNOWN

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state import CmdState
        from oxt.pythonpath.libre_pythonista_lib.cell.state.state_kind import StateKind
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state import CmdState
        from libre_pythonista_lib.cell.state.state_kind import StateKind
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdState(cell=cell, state=StateKind.UNKNOWN)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state_del import CmdStateDel
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state_del import CmdStateDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdStateDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_state import QryState
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_state import QryState

    cell = mocker.MagicMock()

    qry = QryState(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
