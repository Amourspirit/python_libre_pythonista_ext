from __future__ import annotations

from typing import cast, TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_cell_code(loader, py_src_uri) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.cache import MemCache

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache import QryCellCache

    else:
        from libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
        from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache import QryCellCache

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        uri = py_src_uri(cell)
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()

        qry_cache = QryCellCache(cell=cell)
        cache = cast(MemCache, qry_handler.handle(qry_cache))

        qry = QryCellSrcCode(uri=uri, cell=cell)
        result = qry_handler.handle(qry)
        assert result == ""
        assert cache.hits == 0

        # check cached
        result = qry_handler.handle(qry)
        assert result == ""
        assert cache.hits == 1

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
