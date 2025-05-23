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
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted

    SheetCell = Any


class QryCellIsArrayFormula(QryBase, LogMixin, QryUnoCellT[bool]):
    """
    Checks if the cell formula is a array formula.

    Unlike ``QryCellIsPycArrayFormula`` this query does not check if the formula is a pyc formula.
    """

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done")

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
            if not formula:
                self.log.debug("Cell %s has no formula. Not checking for array formula.", self.cell.AbsoluteName)
                return False
            result = formula.startswith("{") and formula.endswith("}")
            self.log.debug("Cell %s is array formula: %s", self.cell.AbsoluteName, result)
            return result

        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> SheetCell:
        return self._cell
