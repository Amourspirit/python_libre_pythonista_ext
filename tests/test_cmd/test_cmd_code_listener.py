from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_code_listener(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import (
            CmdCodeListener,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_code_cell_listeners import QryCodeCellListeners
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import CmdCodeListener
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
        from libre_pythonista_lib.cq.qry.calc.doc.qry_code_cell_listeners import QryCodeCellListeners
        from libre_pythonista_lib.utils.result import Result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # First set a code name for the cell
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        qry_code_listeners = QryCodeCellListeners(doc)
        listeners = qry_handler.handle(qry_code_listeners)

        # Set code name
        cmd = CmdCodeName(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify code name was set
        qry = QryCodeName(cell=cell)
        code_name_result = qry_handler.handle(qry)
        assert Result.is_success(code_name_result)
        code_name = code_name_result.data

        assert code_name not in listeners

        # Test adding listener
        cmd = CmdCodeListener(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success

        assert code_name in listeners

        # Test undo
        cmd_handler.undo()
        assert code_name not in listeners

        # Test redo
        cmd_handler.redo()
        assert cmd.success
        assert code_name in listeners

        # Test adding listener again (should still succeed but not change state)
        cmd = CmdCodeListener(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert not cmd._state_changed

        assert code_name in listeners

        # Test undo
        cmd_handler.undo()
        # because the last command tried to add listener when one already existed then
        # the undo will not remove the listener
        assert code_name in listeners

        # Test redo
        cmd_handler.redo()
        assert cmd.success

        assert code_name in listeners

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_code_listener_no_code_name(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import (
            CmdCodeListener,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import CmdCodeListener
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        # Try to add listener without setting code name first
        cmd = CmdCodeListener(cell=cell)
        cmd_handler.handle(cmd)
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_code_listener_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import (
            CmdCodeListener,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
            CodeCellListeners,
        )
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import CmdCodeListener
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock an exception during listener addition
        mocker.patch.object(CodeCellListeners, "add_listener", side_effect=Exception("Test exception"))

        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        cmd = CmdCodeListener(cell=cell)
        cmd_handler.handle(cmd)
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)
