from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind


class QryRuleNameKindFromCtlKind(QryBase, QryT[RuleNameKind]):
    """
    Maps a control kind (CtlKind) to its corresponding rule name kind (RuleNameKind).

    This query class provides a mapping between control types and their associated rule name types,
    primarily used for data type validation and processing rules.

    Args:
        ctl_kind (CtlKind): The control kind to map to a rule name kind.
    """

    def __init__(self, ctl_kind: CtlKind) -> None:
        QryBase.__init__(self)
        self._map = self._get_map()
        self._ctl_kind = ctl_kind

    def _get_map(self) -> dict[CtlKind, RuleNameKind]:
        """
        Creates a mapping dictionary between control kinds and rule name kinds.

        Returns:
            dict[CtlKind, RuleNameKind]: Dictionary mapping control kinds to rule name kinds.
        """
        control_map = {
            CtlKind.DATA_FRAME: RuleNameKind.CELL_DATA_TYPE_PD_DF,
            CtlKind.DATA_TABLE: RuleNameKind.CELL_DATA_TYPE_TBL_DATA,
            CtlKind.EMPTY: RuleNameKind.CELL_DATA_TYPE_EMPTY,
            CtlKind.ERROR: RuleNameKind.CELL_DATA_TYPE_ERROR,
            CtlKind.FLOAT: RuleNameKind.CELL_DATA_TYPE_FLOAT,
            CtlKind.IMAGE: RuleNameKind.CELL_DATA_TYPE_CELL_IMG,
            CtlKind.INTEGER: RuleNameKind.CELL_DATA_TYPE_INT,
            CtlKind.MAT_PLT_FIGURE: RuleNameKind.CELL_DATA_TYPE_MP_FIGURE,
            CtlKind.NONE: RuleNameKind.CELL_DATA_TYPE_NONE,
            CtlKind.SERIES: RuleNameKind.CELL_DATA_TYPE_PD_SERIES,
            CtlKind.SIMPLE_CTL: RuleNameKind.CELL_DATA_TYPE_STR,
            CtlKind.STRING: RuleNameKind.CELL_DATA_TYPE_STR,
            CtlKind.UNKNOWN: RuleNameKind.UNKNOWN,
        }
        return control_map

    def execute(self) -> RuleNameKind:
        """
        Executes the query to get the corresponding RuleNameKind for the given CtlKind.

        Returns:
            RuleNameKind: The mapped rule name kind. Returns RuleNameKind.UNKNOWN if no mapping exists.
        """
        return self._map.get(self._ctl_kind, RuleNameKind.UNKNOWN)
