from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_array_ability(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import CmdArrayAbility
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import CmdArrayAbility
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        ch = CmdHandler()
        qry_handler = QryHandler()
        qry = QryArrayAbility(cell=cell)
        assert qry_handler.handle(qry) is False

        # Test setting array ability to True
        cmd = CmdArrayAbility(cell=cell, ability=True)
        ch.handle(cmd)
        assert cmd.success
        assert cmd.cell == cell
        assert qry_handler.handle(qry)

        # Test setting same state (should succeed but not change anything)
        cmd = CmdArrayAbility(cell=cell, ability=True)
        ch.handle(cmd)
        assert cmd.success

        # Test changing to different state
        cmd = CmdArrayAbility(cell=cell, ability=False)
        ch.handle(cmd)
        assert cmd.success

        # Test undo
        cmd.undo()
        assert cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_array_ability_error(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import CmdArrayAbility
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import CmdArrayAbility

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock to simulate an error during execution
        cmd = CmdArrayAbility(cell=cell, ability=True)
        mocker.patch.object(cmd, "_get_state", side_effect=Exception("Test error"))

        cmd.execute()
        assert not cmd.success

        # Test undo when not successful
        cmd.undo()  # Should just log "Undo not needed"
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import CmdArrayAbility
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import CmdArrayAbility
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdArrayAbility, "_get_current_state", return_value=True)

    cmd = CmdArrayAbility(cell=cell, ability=True)
    assert cmd.kind == CalcCmdKind.SIMPLE

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility

    # libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_prop_value.QryCellPropValue
    _ = mocker.patch(
        "libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value.QryCellPropValue.execute",
        return_value=True,
    )

    cell = mocker.MagicMock()

    qry = QryArrayAbility(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET

    assert qry.execute()
