from __future__ import annotations


from typing import Any, TYPE_CHECKING
import contextlib

from com.sun.star.uno import RuntimeException

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryCellIsDeleted(QryBase, QryUnoCellT[bool]):
    """Checks if the cell is deleted."""

    def __init__(self, cell: SheetCell) -> None:
        QryBase.__init__(self)
        self._cell = cell

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
