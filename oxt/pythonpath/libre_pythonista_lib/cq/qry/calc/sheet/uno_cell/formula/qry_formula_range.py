from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from com.sun.star.sheet import SheetCellCursor  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryFormulaRange(QryBase, LogMixin, QryUnoCellT[Result[RangeObj, None] | Result[None, Exception]]):
    """
    Checks if the cell formula is a formula.
    """

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell

    def execute(self) -> Result[RangeObj, None] | Result[None, Exception]:
        """
        Executes the query to get if the cell formula is a array formula.

        Returns:
            bool: True if the cell formula is a array formula, False otherwise.
        """

        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._execute_qry(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for array formula.")
                result = Result.failure(Exception("Cell is deleted."))
                return result
            formula = self.cell.getFormula()
            # return formula.startswith("=")

            cursor = cast("SheetCellCursor", self._cell.getSpreadsheet().createCursorByRange(self._cell))  # type: ignore
            cursor.collapseToCurrentArray()
            ca = cursor.getRangeAddress()
            ro = RangeObj.from_range(ca)
            result = Result.success(ro)
            return result

        except Exception as e:
            self.log.exception("Error executing query")
            result = Result.failure(e)
            return result

    @property
    def cell(self) -> SheetCell:
        return self._cell
