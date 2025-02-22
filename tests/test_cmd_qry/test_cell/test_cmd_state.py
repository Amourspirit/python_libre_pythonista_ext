from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture
from unittest.mock import patch

if __name__ == "__main__":
    pytest.main([__file__])


@pytest.fixture
def mock_object_property(mocker):
    mock = mocker.patch(
        "test_functions.MyObject.property", new_callable=mocker.PropertyMock, return_value="new_property_value"
    )
    return mock


@pytest.fixture
def mock_object_property_exception(mocker: MockerFixture):
    mock = mocker.patch(
        "test_cmd_state.CmdState.property", new_callable=mocker.PropertyMock, return_value="new_property_value"
    )
    return mock


def test_cmd_state(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_state import CmdState
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cell.state.state_kind import StateKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_state import QryState
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_state import CmdState
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cell.state.state_kind import StateKind
        from libre_pythonista_lib.query.calc.sheet.cell.qry_state import QryState
        from libre_pythonista_lib.query.qry_handler import QryHandler

    # _ = mocker.patch("libre_pythonista_lib.cmd.calc.sheet.cell.cmd_state.LogInst")

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        ch = CmdHandler()
        qry_handler = QryHandler()
        qry = QryState(cell=cell)

        # Test setting new state
        cmd = CmdState(cell=cell, state=StateKind.UNKNOWN)
        ch.handle(cmd)
        assert cmd.success
        assert cmd.cell == cell
        assert qry_handler.handle(qry) == StateKind.UNKNOWN

        # Test setting same state (should succeed but not change anything)
        cmd = CmdState(cell=cell, state=StateKind.PY_OBJ)
        ch.handle(cmd)
        assert cmd.success
        assert qry_handler.handle(qry) == StateKind.PY_OBJ

        # Test changing to different state
        cmd = CmdState(cell=cell, state=StateKind.ARRAY)
        ch.handle(cmd)
        assert cmd.success

        assert qry_handler.handle(qry) == StateKind.ARRAY

        # Test undo
        cmd.undo()
        assert cmd.success

        assert qry_handler.handle(qry) == StateKind.PY_OBJ

        # Test failed execution
        cmd = CmdState(cell=cell, state=StateKind.ARRAY)
        mocker.patch.object(cmd, "_get_state", side_effect=AttributeError("Simulated error"))

        ch.handle(cmd)
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_state_kind(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_state import CmdState
        from oxt.pythonpath.libre_pythonista_lib.cell.state.state_kind import StateKind
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_state import CmdState
        from libre_pythonista_lib.cell.state.state_kind import StateKind
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        cmd = CmdState(cell=cell, state=StateKind.UNKNOWN)
        assert cmd.kind == CalcCmdKind.SIMPLE

        cmd.kind = CalcCmdKind.SHEET
        assert cmd.kind == CalcCmdKind.SHEET

    finally:
        if doc is not None:
            doc.close(True)


def test_qry_state_kind(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_state import QryState
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.query.calc.sheet.cell.qry_state import QryState

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        qry = QryState(cell=cell)
        assert qry.kind == CalcQryKind.SIMPLE

        qry.kind = CalcQryKind.SHEET
        assert qry.kind == CalcQryKind.SHEET

    finally:
        if doc is not None:
            doc.close(True)
