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


class QryCtlKindFromRuleNameKind(QryBase, QryT[CtlKind]):
    """
    Maps a RuleNameKind to its corresponding CtlKind.

    This query class provides a mapping between rule name kinds (RuleNameKind) and
    control kinds (CtlKind). It is used to determine the appropriate control type
    based on a given rule name kind.

    Args:
        rule_name_kind (RuleNameKind): The rule name kind to map to a control kind.
    """

    def __init__(self, rule_name_kind: RuleNameKind) -> None:
        QryBase.__init__(self)
        self._map = self._get_map()
        self._rule_name_kind = rule_name_kind

    def _get_map(self) -> dict[RuleNameKind, CtlKind]:
        """
        Creates and returns a mapping dictionary between RuleNameKind and CtlKind.

        Returns:
            dict[RuleNameKind, CtlKind]: A dictionary mapping rule name kinds to control kinds.
        """
        control_map = {
            RuleNameKind.CELL_DATA_TYPE_CELL_IMG: CtlKind.IMAGE,
            RuleNameKind.CELL_DATA_TYPE_EMPTY: CtlKind.EMPTY,
            RuleNameKind.CELL_DATA_TYPE_ERROR: CtlKind.ERROR,
            RuleNameKind.CELL_DATA_TYPE_FLOAT: CtlKind.FLOAT,
            RuleNameKind.CELL_DATA_TYPE_INT: CtlKind.INTEGER,
            RuleNameKind.CELL_DATA_TYPE_MP_FIGURE: CtlKind.MAT_PLT_FIGURE,
            RuleNameKind.CELL_DATA_TYPE_NONE: CtlKind.NONE,
            RuleNameKind.CELL_DATA_TYPE_PD_DF: CtlKind.DATA_FRAME,
            RuleNameKind.CELL_DATA_TYPE_PD_SERIES: CtlKind.SERIES,
            RuleNameKind.CELL_DATA_TYPE_STR: CtlKind.STRING,
            RuleNameKind.CELL_DATA_TYPE_TBL_DATA: CtlKind.DATA_TABLE,
            RuleNameKind.UNKNOWN: CtlKind.UNKNOWN,
        }
        return control_map

    def execute(self) -> CtlKind:
        """
        Executes the query to get the corresponding CtlKind for the given RuleNameKind.

        Returns:
            CtlKind: The mapped control kind. Returns CtlKind.UNKNOWN if no mapping exists.
        """
        return self._map.get(self._rule_name_kind, CtlKind.UNKNOWN)
