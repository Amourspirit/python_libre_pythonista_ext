from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_remove_ctl_props(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.remove.cmd_remove_ctl_props import (
            CmdRemoveCtlProps,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.remove.cmd_remove_ctl_props import CmdRemoveCtlProps
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
        from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames

    doc = None
    try:
        # Setup
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        # Set some test properties
        qry_props = QryPropNames(CtlPropKind.CELL_ARRAY_ABILITY, CtlPropKind.CELL_ADDR)
        prop_names = qry_handler.handle(qry_props)
        test_props = {}
        for i, name in enumerate(prop_names):
            test_props[name] = f"value{i}"
        for name, value in test_props.items():
            cell.set_custom_property(name, value)

        # Create Ctl instance
        ctl = Ctl(cell=cell)
        ctl.ctl_props = (CtlPropKind.CELL_ARRAY_ABILITY, CtlPropKind.CELL_ADDR)

        # Create and execute command
        cmd = CmdRemoveCtlProps(ctl=ctl)
        cmd_handler.handle(cmd)

        # Test execution
        assert cmd.success
        for name in test_props:
            assert not cell.has_custom_property(name)

        # Test undo
        cmd_handler.undo()
        for name, value in test_props.items():
            assert cell.has_custom_property(name)
            assert cell.get_custom_property(name) == value

        # Test validation failure
        invalid_ctl = Ctl(cell=None)  # Missing required attributes
        cmd_invalid = CmdRemoveCtlProps(ctl=invalid_ctl)
        cmd_handler.handle(cmd_invalid)
        assert not cmd_invalid.success

        # Test exception handling during execution
        mock_cell = mocker.MagicMock()
        mock_cell.get_custom_property.side_effect = Exception("Test exception")
        ctl_exception = Ctl(cell=mock_cell)
        ctl_exception.ctl_props = [CtlPropKind.CELL_ARRAY_ABILITY]
        cmd_exception = CmdRemoveCtlProps(ctl=ctl_exception)
        cmd_handler.handle(cmd_exception)
        assert not cmd_exception.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_remove_ctl_props_empty(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.remove.cmd_remove_ctl_props import (
            CmdRemoveCtlProps,
        )
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.remove.cmd_remove_ctl_props import CmdRemoveCtlProps
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

    doc = None
    try:
        # Setup
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        # Create Ctl instance with no properties
        ctl = Ctl(cell=cell)
        ctl.ctl_props = []

        # Create and execute command
        cmd = CmdRemoveCtlProps(ctl=ctl)
        cmd_handler.handle(cmd)

        # Test execution
        assert cmd.success

        # Test undo with no changes
        cmd_handler.undo()
        assert cmd.success

    finally:
        if doc is not None:
            doc.close(True)
