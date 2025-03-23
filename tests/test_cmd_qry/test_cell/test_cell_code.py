from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_cell_code(loader, py_src_uri) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.cache import MemCache

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code import QryCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result

    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code import QryCellSrcCode
        from libre_pythonista_lib.utils.result import Result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        uri = py_src_uri(cell)
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        qry = QryCellSrcCode(cell=cell, uri=uri)
        result = qry_handler.handle(qry)
        assert Result.is_success(result)
        assert result.data == ""

        code = "print('Hello World')"
        cmd = CmdCellSrcCode(uri=uri, cell=cell, code=code)
        cmd_handler.handle(cmd)
        assert cmd.success

        result = qry_handler.handle(qry)
        assert Result.is_success(result)
        assert result.data == code

    finally:
        if not doc is None:
            doc.close(True)
