from __future__ import annotations


from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
else:
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryCellSheetName(QryUnoCellT):
    """Gets the sheet name of the cell."""

    def __init__(self, cell: SheetCell) -> None:
        """Constructor

        Args:
            cell (SheetCell): Cell to query.
        """
        self._cell = cell
        self._kind = CalcQryKind.SIMPLE

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

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
