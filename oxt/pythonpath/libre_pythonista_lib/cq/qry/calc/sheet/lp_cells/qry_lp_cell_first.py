from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet import QryLpCellsBySheet
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet import QryLpCellsBySheet
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryLpCellsFirst(QryBase, LogMixin, QrySheetT[Result[CellObj, None] | Result[None, Exception]]):
    """Query that returns the first LibrePythonista cell found in a sheet."""

    def __init__(self, sheet: CalcSheet) -> None:
        """
        Initialize the query.

        Args:
            sheet (CalcSheet): The sheet to search for LibrePythonista cells.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._sheet = sheet
        self.log.debug("init done for doc %s", sheet.name)

    def _qry_lp_cells_by_sheet(self) -> Dict[CellObj, IndexCellProps]:
        """
        Get all LibrePythonista cells in the sheet.

        Returns:
            Dict[CellObj, IndexCellProps]: Dictionary mapping cells to their properties.

        Raises:
            Exception: If query fails.
        """
        qry = QryLpCellsBySheet(sheet=self._sheet)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def execute(self) -> Result[CellObj, None] | Result[None, Exception]:
        """
        Execute the query to get the first LibrePythonista cell.

        Returns:
            Result: Success with first CellObj found, or Failure with None/Exception if no cells exist or on error.
        """
        try:
            sheet_cells = self._qry_lp_cells_by_sheet()
            if len(sheet_cells) == 0:
                self.log.error("get_first_cell() No cells in sheet")
                return Result.failure(Exception("No cells in sheet"))

            # return first item in sheet_cells
            return Result.success(next(iter(sheet_cells)))
        except Exception as e:
            self.log.exception("Error executing query")
            return Result.failure(e)

    @property
    def sheet(self) -> CalcSheet:
        """The sheet being queried."""
        return self._sheet
