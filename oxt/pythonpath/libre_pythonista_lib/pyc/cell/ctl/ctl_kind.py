from __future__ import annotations
from enum import Enum


class CtlKind(Enum):
    """
    Enum for the different kinds of cell controls.
    """

    # pylint: disable=invalid-name
    # pylint: disable=bad-whitespace
    ERROR = (0, "cell_data_type_error")
    NONE = (1, "cell_data_type_none")
    EMPTY = (2, "cell_data_type_empty")
    SIMPLE_CTL = (3, "cell_data_type_simple_ctl")
    STRING = (4, "cell_data_type_str")
    FLOAT = (5, "cell_data_type_float")
    INTEGER = (6, "cell_data_type_int")
    DATA_FRAME = (7, "cell_data_type_pd_df")
    SERIES = (8, "cell_data_type_pd_series")
    DATA_TABLE = (9, "cell_data_type_tbl_data")
    IMAGE = (10, "cell_data_type_cell_img")
    MAT_PLT_FIGURE = (11, "cell_data_type_mp_figure")

    def __str__(self) -> str:
        return self.value[1]

    def __int__(self) -> int:
        return self.value[0]
