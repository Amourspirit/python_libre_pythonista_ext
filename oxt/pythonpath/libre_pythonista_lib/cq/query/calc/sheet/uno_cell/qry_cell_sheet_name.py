from __future__ import annotations


from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryCellSheetName(QryBase, QryUnoCellT[str]):
    """Gets the sheet name of the cell."""

    def __init__(self, cell: SheetCell) -> None:
        """Constructor

        Args:
            cell (SheetCell): Cell to query.
        """
        QryBase.__init__(self)
        self._cell = cell

    def execute(self) -> str:
        """
        Executes the query to get the sheet name of the cell.

        Returns:
            str: The sheet name if successful, otherwise an empty string.
        """

        return self._cell.Spreadsheet.Name  # type: ignore

    @property
    def cell(self) -> SheetCell:
        return self._cell
