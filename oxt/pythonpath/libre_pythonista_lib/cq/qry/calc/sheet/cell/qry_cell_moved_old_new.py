"""Query to determine if a cell has been moved from its original position."""

from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Union

from ooodev.calc import CalcCell
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryCellMovedOldNew(
    QryBase, LogMixin, QryCellT[Union[Result[Tuple[CellObj, CellObj], None], Result[None, Exception]]]
):
    """
    Query to determine if a cell has been moved from its original position and return both old and new positions.

    Returns a tuple of (old_position, new_position) if the cell was moved, or a failure result if not moved or on error.
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the query with a target cell.

        Args:
            cell (CalcCell): The cell to check for movement.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def execute(self) -> Union[Result[Tuple[CellObj, CellObj], None], Result[None, Exception]]:
        """
        Execute the query to check if cell has moved from its original position.

        Returns:
            Result: Success with tuple (old_position, new_position) if cell moved,
                Failure with None if not moved, or Exception on error.
        """
        try:
            qry_addr = QryAddr(cell=self._cell)
            qry_addr_result = self._execute_qry(qry_addr)
            if Result.is_failure(qry_addr_result):
                self.log.debug("execute() Address not found")
                return Result.failure(Exception("Address not found"))
            old_addr = qry_addr_result.data.cell_obj
            moved = self._cell.cell_obj != old_addr
            if moved:
                return Result.success((old_addr, self._cell.cell_obj))
            return Result.failure(Exception("Cell not moved"))

        except Exception as e:
            self.log.exception("Error executing query: %s", e)
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell being queried.

        Returns:
            CalcCell: The cell instance this query is checking.
        """
        return self._cell
