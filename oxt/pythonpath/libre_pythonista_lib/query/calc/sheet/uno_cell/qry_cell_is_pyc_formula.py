from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.const import FORMULA_PYC
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.const import FORMULA_PYC
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted

    SheetCell = Any


class QryCellIsPycFormula(LogMixin, QryUnoCellT):
    """Checks if the cell formula is a pyc formula."""

    def __init__(self, cell: SheetCell) -> None:
        LogMixin.__init__(self)
        self._cell = cell
        self._kind = CalcQryKind.SIMPLE
        self._query_handler = QryHandler()

    def execute(self) -> bool:
        """
        Executes the query to get if the cell formula is a pyc formula.

        Returns:
            bool: True if the cell formula is a pyc formula, False otherwise.
        """

        try:
            qry_cell_del = QryCellIsDeleted(cell=self.cell)
            if self._query_handler.handle(qry_cell_del):
                self.log.debug("Cell is deleted. Not checking for pyc formula.")
                return False
            formula = self.cell.getFormula()
            if not formula:
                return False
            s = formula.lstrip("{")  # could be a array formula
            s = s.lstrip("=")  # formula may start with one or two equal signs
            return s.startswith(FORMULA_PYC)

        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> SheetCell:
        return self._cell

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
