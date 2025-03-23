from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.const import FORMULA_PYC
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula,
    )
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.const import FORMULA_PYC
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula

    SheetCell = Any


class QryCellIsPycArrayFormula(QryBase, LogMixin, QryUnoCellT[bool]):
    """Checks if the cell formula is a pyc array formula."""

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell

    def _qry_cell_array_formula(self) -> bool:
        """Check if the cell formula is a array formula."""
        qry = QryCellIsArrayFormula(cell=self.cell)
        return self._execute_qry(qry)

    def execute(self) -> bool:
        """
        Executes the query to get if the cell formula is a pyc array formula.

        Returns:
            bool: True if the cell formula is a pyc array formula, False otherwise.
        """

        try:
            if not self._qry_cell_array_formula():
                return False

            formula = self.cell.getFormula()
            s = formula.lstrip("{")
            s = s.lstrip("=")  # formula may start with one or two equal signs
            return s.startswith(FORMULA_PYC)

        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> SheetCell:
        return self._cell
