from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted

    SheetCell = Any


class QryCellIsFormula(QryBase, LogMixin, QryUnoCellT[bool]):
    """
    Checks if the cell formula is a formula.
    """

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query to get if the cell formula is a array formula.

        Returns:
            bool: True if the cell formula is a array formula, False otherwise.
        """

        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._execute_qry(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for array formula.")
                return False
            formula = self.cell.getFormula()
            return formula.startswith("=")

        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> SheetCell:
        return self._cell
