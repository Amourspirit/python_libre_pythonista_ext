"""Query to determine if a cell has been moved from its original position."""

from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcCell

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


class QryCellMoved(QryBase, LogMixin, QryCellT[bool]):
    """
    Query to determine if a cell has been moved from its original position.

    Inherits from QryBase, LogMixin, and QryCellT[bool] to provide query functionality,
    logging capabilities, and cell-specific typing.
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

    def execute(self) -> bool:
        """
        Execute the query to check if the cell has moved.

        Returns:
            bool: True if the cell has moved from its original position, False otherwise
                or if an error occurs during execution.
        """
        try:
            qry_addr = QryAddr(cell=self._cell)
            qry_addr_result = self._execute_qry(qry_addr)
            if Result.is_failure(qry_addr_result):
                self.log.debug("execute() Address not found")
                return False
            prop_addr = qry_addr_result.data.cell_obj
            moved = self._cell.cell_obj != prop_addr
            self.log.debug("execute() Cell moved: %s", moved)
            return moved

        except Exception as e:
            self.log.exception("Error executing query: %s", e)
            return False

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell being queried.

        Returns:
            CalcCell: The cell instance this query is checking.
        """
        return self._cell
