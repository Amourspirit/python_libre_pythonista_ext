from __future__ import annotations
from typing import cast, List, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno

from ooodev.calc import CalcCell

from ...cell.state.ctl_state import CtlState
from .array_base import ArrayBase


if TYPE_CHECKING:
    import pandas as pd


class ArrayDS(ArrayBase):
    """Manages Formula and Array for Pandas Series."""

    def __init__(self, cell: CalcCell) -> None:
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
        s = cast("pd.Series", self.get_data().value)
        series_len = len(s)
        if not series_len:
            return [0, 0]
        if s.name:
            return [series_len + 1, 2]
        return [series_len, 2]
