from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_STATE_RULES_DEFAULT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
else:
    from libre_pythonista_lib.const.cache_const import DOC_STATE_RULES_DEFAULT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules


class QryStateRulesDefault(QryBase, QryT[StateRules]):
    """Query that returns default state rules for a cell."""

    def __init__(self) -> None:
        """Initialize the query."""
        QryBase.__init__(self)

    def execute(self) -> StateRules:
        """
        Execute the query to get default state rules.

        Returns:
            StateRules: A new instance of default state rules.
        """
        return StateRules()

    @property
    def cache_key(self) -> str:
        """
        Get the cache key for this query.

        Returns:
            str: The constant DOC_STATE_RULES_DEFAULT used as cache key.
        """
        return DOC_STATE_RULES_DEFAULT
