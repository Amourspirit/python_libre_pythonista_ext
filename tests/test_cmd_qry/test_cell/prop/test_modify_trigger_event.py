from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_modify_trigger_event(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import (
            CmdModifyTriggerEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_modify_trigger_event import (
            QryModifyTriggerEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event_del import (
            CmdModifyTriggerEventDel,
        )
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import CmdModifyTriggerEvent
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_modify_trigger_event import QryModifyTriggerEvent
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event_del import CmdModifyTriggerEventDel

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()
        qry = QryModifyTriggerEvent(cell=cell)

        # Test empty name (should fail)
        cmd = CmdModifyTriggerEvent(cell=cell, name="")
        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test setting new trigger event
        test_event = "cell_data_type_str"
        cmd = CmdModifyTriggerEvent(cell=cell, name=test_event)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify the trigger event was set
        result = qry_handler.handle(qry)
        assert result == test_event

        # Test setting same trigger event (should succeed but not change anything)
        cmd = CmdModifyTriggerEvent(cell=cell, name=test_event)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == test_event

        # Test changing to different trigger event and then undoing
        new_event = "cell_data_type_int"
        cmd = CmdModifyTriggerEvent(cell=cell, name=new_event)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == new_event

        # Test undo
        cmd.undo()
        result = qry_handler.handle(qry)
        assert result == test_event

        # Test deleting the trigger event
        cmd = CmdModifyTriggerEventDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

        # Test deleting when cell does not have property
        cmd = CmdModifyTriggerEventDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_modify_trigger_event_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import (
            CmdModifyTriggerEvent,
        )
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import CmdModifyTriggerEvent

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock execute to raise an exception
        mocker.patch(
            "libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set.CmdCellPropSet.execute",
            side_effect=Exception("Test exception"),
        )

        cmd = CmdModifyTriggerEvent(cell=cell, name="test_event")
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import (
            CmdModifyTriggerEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import CmdModifyTriggerEvent
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdModifyTriggerEvent, "_get_current_state", return_value="")

    cmd = CmdModifyTriggerEvent(cell=cell, name="cell_data_type_int")
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event_del import (
            CmdModifyTriggerEventDel,
        )
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event_del import CmdModifyTriggerEventDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdModifyTriggerEventDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_modify_trigger_event import (
            QryModifyTriggerEvent,
        )
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_modify_trigger_event import QryModifyTriggerEvent

    cell = mocker.MagicMock()

    qry = QryModifyTriggerEvent(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
