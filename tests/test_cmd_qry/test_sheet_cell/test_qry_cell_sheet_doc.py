from __future__ import annotations

from typing import TYPE_CHECKING
import pytest


if __name__ == "__main__":
    pytest.main([__file__])


def test_qry_cell_sheet_doc(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_sheet_doc import QryCellSheetDoc
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler

    else:
        from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_sheet_doc import QryCellSheetDoc
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache import QryCellCache

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        qry_handler = QryHandler()

        qry_cell = QryCellSheetDoc(cell=cell.component)
        result = qry_handler.handle(qry_cell)
        assert isinstance(result, CalcDoc)

    finally:
        if not doc is None:
            doc.close(True)
