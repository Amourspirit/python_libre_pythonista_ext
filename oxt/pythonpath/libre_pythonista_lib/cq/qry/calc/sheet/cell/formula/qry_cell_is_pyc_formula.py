from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import (
        QryCellIsPycFormula as UnoQryCellIsPycFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase

else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import (
        QryCellIsPycFormula as UnoQryCellIsPycFormula,
    )
    from libre_pythonista_lib.cq.qry.qry_base import QryBase


class QryCellIsPycFormula(QryBase, QryCellT[bool]):
    """Checks if the cell formula is a pyc formula."""

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the query.

        Args:
            cell (CalcCell): The cell to check for pyc formula.
        """
        QryBase.__init__(self)
        self._cell = cell

    def _qry_cell_deleted(self) -> bool:
        """
        Check if the cell has been deleted.

        Returns:
            bool: True if the cell has been deleted, False otherwise.
        """
        qry = QryCellIsDeleted(cell=self.cell)
        return self._execute_qry(qry)

    def execute(self) -> bool:
        """
        Execute the query to check if cell contains a pyc formula.

        Returns:
            bool: True if the cell contains a pyc formula, False otherwise.
        """
        qry = UnoQryCellIsPycFormula(cell=self._cell.component)
        return self._execute_qry(qry)

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell being queried.

        Returns:
            CalcCell: The cell instance.
        """
        return self._cell
