from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_array_formula import (
        QryCellIsPycArrayFormula as UnoQryCellIsPycArrayFormula,
    )
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_array_formula import (
        QryCellIsPycArrayFormula as UnoQryCellIsPycArrayFormula,
    )


class QryCellIsPycArrayFormula(QryBase, QryCellT[bool]):
    """Checks if the cell formula is a pyc array formula."""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query to get if the cell formula is a pyc array formula.

        Returns:
            bool: True if the cell formula is a pyc array formula, False otherwise.
        """

        qry_cell_del = UnoQryCellIsPycArrayFormula(cell=self.cell.component)
        return self._execute_qry(qry_cell_del)

    @property
    def cell(self) -> CalcCell:
        return self._cell
