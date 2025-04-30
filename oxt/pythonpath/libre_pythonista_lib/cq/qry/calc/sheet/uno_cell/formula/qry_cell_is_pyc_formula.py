from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.const import FORMULA_PYC
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.const import FORMULA_PYC
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted

    SheetCell = Any


class QryCellIsPycFormula(QryBase, LogMixin, QryUnoCellT[bool]):
    """Checks if the cell formula is a pyc formula."""

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done")

    def execute(self) -> bool:
        """
        Executes the query to get if the cell formula is a pyc formula.

        Returns:
            bool: True if the cell formula is a pyc formula, False otherwise.
        """

        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._execute_qry(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for pyc formula.")
                return False
            formula = self.cell.getFormula()
            if not formula:
                self.log.debug("Cell %s has no formula. Not checking for pyc formula.", self.cell.AbsoluteName)
                return False
            s = formula.lstrip("{")  # could be a array formula
            s = s.lstrip("=")  # formula may start with one or two equal signs
            result = s.startswith(FORMULA_PYC)
            self.log.debug("Cell %s is pyc formula: %s", self.cell.AbsoluteName, result)
            return result

        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> SheetCell:
        return self._cell
