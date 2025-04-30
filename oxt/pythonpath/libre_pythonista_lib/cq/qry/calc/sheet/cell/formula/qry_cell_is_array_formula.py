from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula as UnoQryCellIsArrayFormula,
    )
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula as UnoQryCellIsArrayFormula,
    )


class QryCellIsArrayFormula(QryBase, QryCellT[bool]):
    """
    Checks if the cell formula is a array formula.

    Unlike ``QryCellIsPycArrayFormula`` this query does not check if the formula is a pyc formula.
    """

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query to get if the cell formula is a array formula.

        Returns:
            bool: True if the cell formula is a array formula, False otherwise.
        """

        qry_cell_del = UnoQryCellIsArrayFormula(cell=self.cell.component)
        return self._execute_qry(qry_cell_del)

    @property
    def cell(self) -> CalcCell:
        return self._cell
