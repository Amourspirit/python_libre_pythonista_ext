from __future__ import annotations
from typing import Any, TYPE_CHECKING, Union

from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from com.sun.star.sheet import SheetCellCursor  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_cursor import (
        QryFormulaCursor,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_cursor import QryFormulaCursor
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryFormulaRange(QryBase, LogMixin, QryUnoCellT[Union[Result[RangeObj, None], Result[None, Exception]]]):
    """
    Get the range of the cell's array formula.
    """

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done")

    def _qry_formula_cursor(self) -> SheetCellCursor:
        """Get the cursor for the cell's array formula range."""
        qry = QryFormulaCursor(cell=self.cell)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

    def execute(self) -> Union[Result[RangeObj, None], Result[None, Exception]]:
        """
        Executes the query to get the range of the cell's array formula.

        Returns:
            Result: The range of the cell's array formula if successful, otherwise an exception.
        """

        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._execute_qry(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for array formula.")
                result = Result.failure(Exception("Cell is deleted."))
                return result

            cursor = self._qry_formula_cursor()
            ca = cursor.getRangeAddress()
            ro = RangeObj.from_range(ca)
            result = Result.success(ro)
            self.log.debug("Formula range %s, for cell %s", ro, self.cell.AbsoluteName)
            return result

        except Exception as e:
            self.log.exception("Error executing query: %s", e)
            result = Result.failure(e)
            return result

    @property
    def cell(self) -> SheetCell:
        """The cell being queried"""
        return self._cell
