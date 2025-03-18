from __future__ import annotations
from typing import Any, TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_append_code(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_cell_code import QryCellCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.code.py_module import PyModule
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_cell_code import QryCellCode
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    doc = None
    try:
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        mod = PyModule()

        # Test appending initial code
        initial_code = "x = 42"
        cmd = CmdAppendCode(cell=cell, mod=mod, code=initial_code)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify code was added
        py_src_mgr = cmd._get_py_src_mgr()
        assert py_src_mgr[cell.cell_obj].source_code == initial_code

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) == initial_code

        # Test appending additional code
        additional_code = "y = x + 10"
        cmd = CmdUpdateCode(cell=cell, mod=mod, code=additional_code)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify both codes are present
        assert py_src_mgr[cell.cell_obj].source_code == additional_code

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) == additional_code

        # Test undo
        cmd_handler.undo()
        assert py_src_mgr[cell.cell_obj].source_code == initial_code

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) == initial_code

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_append_code_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    else:
        from libre_pythonista_lib.code.py_module import PyModule
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        mod = PyModule()

        # Mock an exception during execution
        mocker.patch(
            "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager.PySourceManager.add_source",
            side_effect=Exception("Test exception"),
        )

        cmd = CmdAppendCode(cell=cell, mod=mod, code="x = 42")
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_append_code_empty(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_cell_code import QryCellCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.code.py_module import PyModule
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_cell_code import QryCellCode
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    doc = None
    try:
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        mod = PyModule()

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) is None

        # Test appending empty code
        cmd = CmdAppendCode(cell=cell, mod=mod, code="")
        cmd_handler.handle(cmd)
        assert cmd.success

        py_src_mgr = cmd._get_py_src_mgr()
        assert py_src_mgr[cell.cell_obj].source_code == ""

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) == ""

        cmd_handler.undo()

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) is None

        cmd_handler.redo()

        qry = QryCellCode(cell=cell, mod=mod)
        assert qry_handler.handle(qry) == ""

    finally:
        if doc is not None:
            doc.close(True)
