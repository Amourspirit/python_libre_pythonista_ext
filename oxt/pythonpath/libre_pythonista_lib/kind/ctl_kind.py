from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind

# see Also: cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind.QryCtlKindFromRuleNameKind
# see Also: cq.qry.calc.common.map.qry_rule_name_kind_from_ctl_kind.QryRuleNameKindFromCtlKind


class CtlKind(Enum):
    """
    Enum for the different kinds of cell controls.
    """

    # pylint: disable=invalid-name
    # pylint: disable=bad-whitespace
    DATA_FRAME = (8, "cell_data_type_pd_df")
    DATA_TABLE = (10, "cell_data_type_tbl_data")
    EMPTY = (3, "cell_data_type_empty")
    ERROR = (1, "cell_data_type_error")
    FLOAT = (6, "cell_data_type_float")
    IMAGE = (11, "cell_data_type_cell_img")
    INTEGER = (7, "cell_data_type_int")
    MAT_PLT_FIGURE = (12, "cell_data_type_mp_figure")
    NONE = (2, "cell_data_type_none")
    SERIES = (9, "cell_data_type_pd_series")
    SIMPLE_CTL = (4, "cell_data_type_simple_ctl")
    STRING = (5, "cell_data_type_str")
    UNKNOWN = (0, "unknown")

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
