from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager


# tested in: tests/test_cmd/test_cmd_append_code.py


class QryPySrcMgrCode(QryBase, QryCellT[PySourceManager]):
    def __init__(self, cell: CalcCell, mod: PyModuleT) -> None:
        QryBase.__init__(self)
        self._cell = cell
        self._mod = mod

    def execute(self) -> PySourceManager:
        """
        Executes the query to retrieve the source code for the cell.

        Returns:
            str | None: The source code if found, None if the cell has no associated code or on error
        """
        return PySourceManager(doc=self.cell.calc_doc, mod=self._mod)

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell associated with this query.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
