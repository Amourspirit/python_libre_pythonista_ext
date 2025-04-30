from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.utils.result import Result

    SheetCell = Any


class QryCellFormula(QryBase, LogMixin, QryUnoCellT[Result[str, None] | Result[None, Exception]]):
    """Query to get a cell's formula without array formula markers and leading/trailing whitespace."""

    def __init__(self, cell: SheetCell) -> None:
        """
        Initialize the query with a cell.

        Args:
            cell (SheetCell): The LibreOffice Calc cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done")

    def execute(self) -> Result[str, None] | Result[None, Exception]:
        """
        Execute the query to get the cell's formula.

        Returns:
            Result: Success with formula string if found, or Failure with None/Exception if:
                - Cell is deleted
                - Cell has no formula
                - Error occurs during execution
        """
        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._execute_qry(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for array formula.")
                return Result.failure(Exception("Cell is deleted."))
            formula = self.cell.getFormula()
            if not formula:
                self.log.debug("Cell %s has no formula. Not checking for array formula.", self.cell.AbsoluteName)
                return Result.failure(Exception("Cell has no formula."))
            result = formula.lstrip("{").rstrip("}").lstrip("= ").rstrip()
            self.log.debug("Cell %s is formula: %s", self.cell.AbsoluteName, result)
            return Result.success(result)

        except Exception as e:
            self.log.exception("Error executing query: %s", e)
            return Result.failure(e)

    @property
    def cell(self) -> SheetCell:
        """The LibreOffice Calc cell being queried."""
        return self._cell
