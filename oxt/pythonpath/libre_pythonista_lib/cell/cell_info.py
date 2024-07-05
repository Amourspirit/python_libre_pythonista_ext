from __future__ import annotations
from typing import TYPE_CHECKING
import contextlib
import uno
from ooodev.utils.data_type.cell_obj import CellObj
from com.sun.star.uno import RuntimeException

from ..ex import CellDeletedError
from ..const import FORMULA_PYC

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service


class CellInfo:
    """Gets info about a cell that is specific to this extension."""

    def __init__(self, cell: SheetCell):
        """Initializes the instance with the cell to get info from."""
        self.cell = cell

    def is_pyc_formula(self) -> bool:
        """
        Returns True if the cell contains a pyc formula.

        Raises:
            CellDeletedError: If the cell has been deleted.

        Returns:
            bool: True if the cell contains a pyc formula.
        """
        global FORMULA_PYC  # COM.GITHUB.AMOURSPIRIT.EXTENSION.LIBREPYTHONISTA.PYIMPL.PYC
        if self.is_cell_deleted():
            raise CellDeletedError("Cell is deleted.")
        formula = self.cell.getFormula()
        if not formula:
            return False
        s = formula.lstrip("{")  # could be a array formula
        s = s.lstrip("=")  # formula may start with one or two equal signs
        return s.startswith(FORMULA_PYC)

    def is_cell_deleted(self) -> bool:
        """Returns True if the cell has been deleted."""
        with contextlib.suppress(RuntimeException):
            _ = self.cell.AbsoluteName
            return False
        return True

    def get_cell_obj(self) -> CellObj:
        """
        Returns a CellObj instance for the cell.

        Raises:
            CellDeletedError: If the cell has been deleted.

        Returns:
            CellObj: A CellObj instance for the cell.
        """
        if self.is_cell_deleted():
            raise CellDeletedError("Cell is deleted.")
        addr = self.cell.getCellAddress()
        return CellObj.from_idx(col_idx=addr.Column, row_idx=addr.Row, sheet_idx=addr.Sheet)
