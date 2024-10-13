from __future__ import annotations
from typing import Any, cast, List

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno

from ooodev.calc import CalcCell

from ...cell.state.ctl_state import CtlState
from .array_base import ArrayBase


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

    @override
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
