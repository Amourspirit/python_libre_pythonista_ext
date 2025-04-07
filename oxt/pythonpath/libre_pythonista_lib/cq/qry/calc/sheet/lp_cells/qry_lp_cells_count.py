from __future__ import annotations

from typing import TYPE_CHECKING, Dict
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet import QryLpCellsBySheet
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet import QryLpCellsBySheet
    from libre_pythonista_lib.utils.result import Result


class QryLpCellsCount(QryBase, LogMixin, QrySheetT[Result[int, None] | Result[None, Exception]]):
    """
    Query that counts the number of LibrePythonista cells in a sheet.

    Inherits from QryBase, LogMixin, and QrySheetT with a Result type that can be either
    a success with int count or a failure with None/Exception.
    """

    def __init__(self, sheet: CalcSheet) -> None:
        """
        Initialize the query with a CalcSheet.

        Args:
            sheet (CalcSheet): The sheet to count LibrePythonista cells in.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._sheet = sheet
        self.log.debug("init done for doc %s", sheet.name)

    def _qry_lp_cells_by_sheet(self) -> Dict[CellObj, IndexCellProps]:
        """
        Helper method that queries all LibrePythonista cells in the sheet.

        Returns:
            Dict[CellObj, IndexCellProps]: Dictionary mapping cells to their properties.

        Raises:
            Exception: If the query fails.
        """
        qry = QryLpCellsBySheet(sheet=self._sheet)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def execute(self) -> Result[int, None] | Result[None, Exception]:
        """
        Execute the query to count LibrePythonista cells.

        Returns:
            Result: Success with count of cells, or Failure with Exception.
        """
        try:
            return Result.success(len(self._qry_lp_cells_by_sheet()))
        except Exception as e:
            return Result.failure(e)
