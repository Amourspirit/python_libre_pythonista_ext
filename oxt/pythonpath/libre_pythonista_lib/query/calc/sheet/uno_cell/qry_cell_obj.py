from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.ex.exceptions import CellDeletedError
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
else:
    from libre_pythonista_lib.query.qry_base import QryBase
    from libre_pythonista_lib.ex.exceptions import CellDeletedError
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_uno_cell_t import QryUnoCellT
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted

    SheetCell = Any


class QryCellObj(QryBase, QryUnoCellT[CellObj]):
    """Gets the cell object."""

    def __init__(self, cell: SheetCell) -> None:
        """Constructor

        Args:
            cell (SheetCell): Cell to query.
        """
        QryBase.__init__(self)
        self._cell = cell

    def execute(self) -> CellObj:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        qry_cell_del = QryCellIsDeleted(cell=self.cell)
        if self._execute_qry(qry_cell_del):
            raise CellDeletedError("Cell is deleted.")

        addr = self.cell.getCellAddress()
        return CellObj.from_idx(col_idx=addr.Column, row_idx=addr.Row, sheet_idx=addr.Sheet)

    @property
    def cell(self) -> SheetCell:
        return self._cell
