from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_cell_props_set(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_props_set import CmdCellPropsSet
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_props_set import CmdCellPropsSet
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        # Test setting multiple properties
        props = {"test_prop1": "value1", "test_prop2": 42, "test_prop3": True}
        cmd = CmdCellPropsSet(cell=cell, **props)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify properties were set
        for name, value in props.items():
            assert cell.has_custom_property(name)
            assert cell.get_custom_property(name) == value

        # Test undo
        cmd_handler.handle_undo(cmd)
        for name in props:
            assert not cell.has_custom_property(name)

        # Test setting properties when some already exist
        cell.set_custom_property("existing_prop", "old_value")
        props = {"existing_prop": "new_value", "new_prop": "value"}
        cmd = CmdCellPropsSet(cell=cell, **props)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert cell.get_custom_property("existing_prop") == "new_value"
        assert cell.get_custom_property("new_prop") == "value"

        # Test undo with existing properties
        cmd_handler.undo()
        assert cell.get_custom_property("existing_prop") == "old_value"
        assert not cell.has_custom_property("new_prop")

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_cell_props_set_error(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_props_set import CmdCellPropsSet
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_props_set import CmdCellPropsSet

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Test error during property setting
        props = {"test_prop": "value"}
        cmd = CmdCellPropsSet(cell=cell, **props)
        mocker.patch.object(cell, "set_custom_property", side_effect=Exception("Simulated error"))

        cmd.execute()
        assert not cmd.success
        assert not cell.has_custom_property("test_prop")

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_props_set import CmdCellPropsSet
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_props_set import CmdCellPropsSet
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()
    cmd = CmdCellPropsSet(cell=cell, test_prop="value")
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET
