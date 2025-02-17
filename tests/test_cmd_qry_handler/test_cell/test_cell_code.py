from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_cell_code(loader, py_src_uri) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache import (
            QryHandlerCellCache,
        )
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_handler_cell_cache import CmdHandlerCellCache
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache import (
            QryHandlerCellCache,
        )
    else:
        from libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache import QryHandlerCellCache
        from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_handler_cell_cache import CmdHandlerCellCache
        from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache import QryHandlerCellCache

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        uri = py_src_uri(cell)
        cmd_handler = CmdHandlerCellCache()
        qry_handler = QryHandlerCellCache()

        qry = QryCellSrcCode(uri=uri, cell=cell)
        result = qry_handler.handle(qry)
        assert result == ""

        # check cached
        result = qry_handler.handle(qry)
        assert result == ""

        code = "print('Hello World')"
        cmd = CmdCellSrcCode(uri=uri, cell=cell, code=code)
        cmd_handler.handle(cmd)
        assert cmd.success

        result = qry_handler.handle(qry)
        assert result == code

        result2 = qry_handler.handle(qry)
        assert result2 == result

    finally:
        if not doc is None:
            doc.close(True)
