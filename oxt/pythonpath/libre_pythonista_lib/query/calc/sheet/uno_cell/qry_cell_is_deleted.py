from __future__ import annotations


from typing import Any, TYPE_CHECKING
import contextlib

from com.sun.star.uno import RuntimeException

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
else:
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryCellIsDeleted(QryUnoCellT):
    """Checks if the cell is deleted."""

    def __init__(self, cell: SheetCell) -> None:
        self._cell = cell
        self._kind = CalcQryKind.SIMPLE

    def execute(self) -> bool:
        """
        Executes the query to get if the cell is deleted.

        Returns:
            bool: True if the cell is deleted, False otherwise.
        """

        with contextlib.suppress(RuntimeException):
            _ = self.cell.AbsoluteName
            return False
        return True

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
