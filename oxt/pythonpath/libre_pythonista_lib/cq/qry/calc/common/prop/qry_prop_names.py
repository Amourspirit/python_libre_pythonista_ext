from __future__ import annotations

from typing import Set, cast, TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
else:
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind

# tested in: tests/test_cmd_qry/test_common/test_style/test_ctl/test_qry_prop_names.py


class QryPropNames(QryBase, QryT[Set[str]]):
    """
    A query class that retrieves property names based on a given control property kind.
    Inherits from QryBase and implements QryT with a return type of Set[str].
    """

    def __init__(self, *prop_kind: CtlPropKind) -> None:
        """
        Initialize the query with a control properties kind.

        Args:
            prop_kind (CtlPropKind): One or more kind of control property to query.
        """
        QryBase.__init__(self)
        self._prop_kind = prop_kind
        self._keys = cast("KeyMaker", None)

    def _get_keys(self) -> KeyMaker:
        """
        Internal method to get KeyMaker instance by executing QryKeyMaker.

        Returns:
            KeyMaker: An instance of KeyMaker containing property keys.
        """
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def execute(self) -> Set[str]:
        """
        Execute the query to get property names based on the initialized property kind.

        Returns:
            Set[str]: A set containing the property name(s) corresponding to the property kind.
        """
        if self._keys is None:
            self._keys = self._get_keys()

        result: Set[str] = set()
        for kind in self._prop_kind:
            if kind == CtlPropKind.CTL_STATE:
                result.add(self._keys.ctl_state_key)
            elif kind == CtlPropKind.CTL_SHAPE:
                result.add(self._keys.ctl_shape_key)
            elif kind == CtlPropKind.CELL_ADDR:
                result.add(self._keys.cell_addr_key)
            elif kind == CtlPropKind.CTL_ORIG:
                result.add(self._keys.ctl_orig_ctl_key)
            elif kind == CtlPropKind.CELL_ARRAY_ABILITY:
                result.add(self._keys.cell_array_ability_key)
            elif kind == CtlPropKind.MODIFY_TRIGGER_EVENT:
                result.add(self._keys.modify_trigger_event)
            elif kind == CtlPropKind.PYC_RULE:
                result.add(self._keys.pyc_rule_key)
        return result
