from __future__ import annotations
from enum import Enum


class RuleNameKind(Enum):
    """
    Enum for the different kinds of cell control properties.
    """

    CELL_DATA_TYPE_SIMPLE_CTL = "cell_data_type_simple_ctl"
    CELL_DATA_TYPE_MP_FIGURE = "cell_data_type_mp_figure"
    CELL_DATA_TYPE_CELL_IMG = "cell_data_type_cell_img"
    CELL_DATA_TYPE_STR = "cell_data_type_str"
    CELL_DATA_TYPE_NONE = "cell_data_type_none"
    CELL_DATA_TYPE_EMPTY = "cell_data_type_empty"
    CELL_DATA_TYPE_ERROR = "cell_data_type_error"
    CELL_DATA_TYPE_INT = "cell_data_type_int"
    CELL_DATA_TYPE_TBL_DATA = "cell_data_type_tbl_data"
    CELL_DATA_TYPE_FLOAT = "cell_data_type_float"
    CELL_DATA_TYPE_PD_DF = "cell_data_type_pd_df"
    CELL_DATA_TYPE_PD_SERIES = "cell_data_type_pd_series"

    def __str__(self) -> str:
        return self.value
