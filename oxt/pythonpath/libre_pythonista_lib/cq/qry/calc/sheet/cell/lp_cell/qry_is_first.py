from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_first import QryLpCellsFirst
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_first import QryLpCellsFirst
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryIsFirst(QryBase, LogMixin, QryCellT[Result[bool, None] | Result[None, Exception]]):
    """
    Query to determine if a given cell is the first LibrePythonista cell in a sheet.

    Inherits from QryBase, LogMixin, and QryCellT with a Result type that can be either
    a boolean success or None/Exception failure.
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the query with a target cell.

        Args:
            cell (CalcCell): The cell to check if it's first
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_lp_cells_first(self) -> CellObj:
        """
        Query to get the first LibrePythonista cell in the sheet.

        Returns:
            CellObj: Cell object representing the first LP cell

        Raises:
            Exception: If query fails to find first cell
        """
        qry = QryLpCellsFirst(sheet=self._cell.calc_sheet)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def execute(self) -> Result[bool, None] | Result[None, Exception]:
        """
        Execute the query to check if the cell is first.

        Returns:
            Result: Success with boolean indicating if cell is first,
                or Failure with Exception
        """
        try:
            first_cell = self._qry_lp_cells_first()
            result = first_cell == self.cell.cell_obj
            self.log.debug("is first cell: %s", result)
            return Result.success(result)
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell being queried.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
