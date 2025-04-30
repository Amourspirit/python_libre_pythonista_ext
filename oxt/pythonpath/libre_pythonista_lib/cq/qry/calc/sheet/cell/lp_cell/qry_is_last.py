from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_last import QryLpCellLast
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_last import QryLpCellLast
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryIsLast(QryBase, LogMixin, QryCellT[Result[bool, None] | Result[None, Exception]]):
    """
    Query to determine if a given cell is the last LibrePythonista cell in a sheet.

    Inherits from QryBase, LogMixin, and QryCellT with a Result type that can be either
    a boolean success or None/Exception failure.
    """

    def __init__(self, cell: CalcCell, from_sheet: bool = False) -> None:
        """
        Initialize the query with a target cell.

        Args:
            cell (CalcCell): The cell to check if it's last
            from_sheet (bool, optional): If True, gets cells directly from sheet. If False, gets from Python source manager. Defaults to False
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._from_sheet = from_sheet
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_lp_cells_last(self) -> CellObj:
        """
        Query to get the last LibrePythonista cell in the sheet.

        Returns:
            CellObj: Cell object representing the last LP cell

        Raises:
            Exception: If query fails to find last cell
        """
        qry = QryLpCellLast(sheet=self._cell.calc_sheet, from_sheet=self._from_sheet)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def execute(self) -> Result[bool, None] | Result[None, Exception]:
        """
        Execute the query to check if the cell is last.

        Returns:
            Result: Success with boolean indicating if cell is last,
                or Failure with Exception
        """
        try:
            first_cell = self._qry_lp_cells_last()
            result = first_cell == self.cell.cell_obj
            self.log.debug("is last cell: %s", result)
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
