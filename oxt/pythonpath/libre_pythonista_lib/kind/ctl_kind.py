from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind


class CtlKind(Enum):
    """
    Enum for the different kinds of cell controls.
    """

    # pylint: disable=invalid-name
    # pylint: disable=bad-whitespace
    UNKNOWN = (0, "unknown")
    ERROR = (1, "cell_data_type_error")
    NONE = (2, "cell_data_type_none")
    EMPTY = (3, "cell_data_type_empty")
    SIMPLE_CTL = (4, "cell_data_type_simple_ctl")
    STRING = (5, "cell_data_type_str")
    FLOAT = (6, "cell_data_type_float")
    INTEGER = (7, "cell_data_type_int")
    DATA_FRAME = (8, "cell_data_type_pd_df")
    SERIES = (9, "cell_data_type_pd_series")
    DATA_TABLE = (10, "cell_data_type_tbl_data")
    IMAGE = (11, "cell_data_type_cell_img")
    MAT_PLT_FIGURE = (12, "cell_data_type_mp_figure")

    def __str__(self) -> str:
        return self.value[1]

    def __int__(self) -> int:
        return self.value[0]

    @staticmethod
    def from_str(s: str) -> CtlKind:
        """
        Converts a string to a CtlKind.

        Returns CtlKind.UNKNOWN if the string is not a valid CtlKind.
        """
        for kind in CtlKind:
            if kind.value[1] == s:
                return kind
        return CtlKind.UNKNOWN

    @staticmethod
    def from_rule_name_kind(rule_name_kind: RuleNameKind) -> CtlKind:
        """
        Converts a RuleNameKind to a CtlKind.

        Returns CtlKind.UNKNOWN if the RuleNameKind is not a valid CtlKind.
        """
        if not TYPE_CHECKING:
            from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        s = str(rule_name_kind)
        for kind in CtlKind:
            if kind.value[1] == s:
                return kind
        return CtlKind.UNKNOWN
