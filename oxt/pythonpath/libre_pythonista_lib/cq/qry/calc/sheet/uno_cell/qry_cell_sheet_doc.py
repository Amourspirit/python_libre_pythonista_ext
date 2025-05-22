from __future__ import annotations


from typing import Any, TYPE_CHECKING, Union
from ooodev.calc import CalcDoc

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT

    SheetCell = Any


class QryCellSheetDoc(QryBase, QryUnoCellT[Union[CalcDoc, None]]):
    """Gets the sheet document of the cell."""

    def __init__(self, cell: SheetCell) -> None:
        """Constructor

        Args:
            cell (SheetCell): Cell to query.
        """
        QryBase.__init__(self)
        self._cell = cell

    def execute(self) -> Union[CalcDoc, None]:
        """
        Executes the query to get the sheet document of the cell.

        Returns:
            CalcDoc, None: The sheet document if successful, otherwise None.
        """
        return CalcDoc.from_obj(obj=self._cell.Spreadsheet)  # type: ignore

    @property
    def cell(self) -> SheetCell:
        return self._cell
