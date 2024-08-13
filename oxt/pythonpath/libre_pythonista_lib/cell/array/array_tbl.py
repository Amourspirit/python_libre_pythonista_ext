from __future__ import annotations
from typing import Any, cast, List, TYPE_CHECKING
import uno

from ooodev.calc import CalcCell

from ...cell.state.ctl_state import CtlState
from .array_base import ArrayBase


if TYPE_CHECKING:
    import pandas as pd
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger

else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class ArrayTbl(ArrayBase):
    """Manages Formula and Array for Pandas Series."""

    def __init__(self, cell: CalcCell):
        """
        Constructor

        Args:
            cell (CalcCell): Calc Cell
        """
        ArrayBase.__init__(self, cell)
        self._ctl_state = CtlState(cell)

    def get_rows_cols(self) -> List[int]:
        """
        Gets the number of rows and columns for a DataFrame.

        Returns:
            List[int]: Number of rows and columns
        """
        dd = self.get_data().dd_data

        lst_data = cast(List[List[Any]], dd.data)
        rows = len(lst_data)
        if rows == 0:
            return [0, 0]
        first = lst_data[0]
        cols = len(first)
        return [rows, cols]
