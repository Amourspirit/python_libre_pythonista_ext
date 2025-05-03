from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Union


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
    SheetCellCursor = Any


class QryFormulaCursor(QryBase, LogMixin, QryUnoCellT[Union[Result[SheetCellCursor, None], Result[None, Exception]]]):
    """
    Query to create a cursor for a cell's array formula range.

    Inherits from QryBase, LogMixin, and QryUnoCellT with a Result type that can contain either
    a SheetCellCursor or None, or an Exception in case of failure.
    """

    def __init__(self, cell: SheetCell) -> None:
        """
        Initialize the query with a cell.

        Args:
            cell (SheetCell): The LibreOffice Calc cell to query
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done")

    def execute(self) -> Union[Result[SheetCellCursor, None], Result[None, Exception]]:
        """
        Execute the query to get a cursor for the cell's array formula range.

        Returns:
            Result containing either:
            - Success: SheetCellCursor positioned at the array formula range
            - Failure: None if cell is deleted, or Exception if error occurs
        """
        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._execute_qry(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for array formula.")
                result = Result.failure(Exception("Cell is deleted."))
                return result

            cursor = cast("SheetCellCursor", self._cell.getSpreadsheet().createCursorByRange(self._cell))  # type: ignore
            if cursor is None:
                self.log.debug("Cursor is None for cell %s", self.cell.AbsoluteName)
                result = Result.failure(Exception("Cursor is None."))
                return result
            cursor.collapseToCurrentArray()
            result = Result.success(cursor)
            self.log.debug("Formula Cursor created for cell %s", self.cell.AbsoluteName)
            return result

        except Exception as e:
            self.log.exception("Error executing query: %s", e)
            return Result.failure(e)

    @property
    def cell(self) -> SheetCell:
        """
        The cell being queried.

        Returns:
            SheetCell: The LibreOffice Calc cell instance
        """
        return self._cell
