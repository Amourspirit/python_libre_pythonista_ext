from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind


# see Also: cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind.QryCtlKindFromRuleNameKind
# see Also: cq.qry.calc.common.map.qry_rule_name_kind_from_ctl_kind.QryRuleNameKindFromCtlKind
class RuleNameKind(Enum):
    """
    Enum for the different kinds of cell control properties.
    """

    CELL_DATA_TYPE_CELL_IMG = "cell_data_type_cell_img"
    CELL_DATA_TYPE_EMPTY = "cell_data_type_empty"
    CELL_DATA_TYPE_ERROR = "cell_data_type_error"
    CELL_DATA_TYPE_FLOAT = "cell_data_type_float"
    CELL_DATA_TYPE_INT = "cell_data_type_int"
    CELL_DATA_TYPE_MP_FIGURE = "cell_data_type_mp_figure"
    CELL_DATA_TYPE_NONE = "cell_data_type_none"
    CELL_DATA_TYPE_PD_DF = "cell_data_type_pd_df"
    CELL_DATA_TYPE_PD_SERIES = "cell_data_type_pd_series"
    CELL_DATA_TYPE_SIMPLE_CTL = "cell_data_type_simple_ctl"
    CELL_DATA_TYPE_STR = "cell_data_type_str"
    CELL_DATA_TYPE_TBL_DATA = "cell_data_type_tbl_data"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_str(s: str) -> RuleNameKind:
        """Converts a string to a RuleNameKind."""
        for kind in RuleNameKind:
            if kind.value == s:
                return kind
        return RuleNameKind.UNKNOWN

    @staticmethod
    def from_ctl_kind(ctl_kind: CtlKind) -> RuleNameKind:
        """Converts a CtlKind to a RuleNameKind."""
        if not TYPE_CHECKING:
            from libre_pythonista_lib.kind.ctl_kind import CtlKind
        s = str(ctl_kind)
        for kind in RuleNameKind:
            if kind.value == s:
                return kind
        return RuleNameKind.UNKNOWN
