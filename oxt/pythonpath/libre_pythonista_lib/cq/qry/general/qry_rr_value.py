from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_resource_resolver import QryResourceResolver
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.general.qry_resource_resolver import QryResourceResolver


class QryRRValue(QryBase, QryT[str]):
    """Gets the value from the resource resolver"""

    def __init__(self, res_key: str) -> None:
        """Constructor

        Args:
            res_key (str): Resource key to query.
        """
        QryBase.__init__(self)
        self._res_key = res_key

    def execute(self) -> str:
        """
        Executes the query and returns the value.

        Returns:
            str: Value from the resource resolver.
        """
        qry = QryResourceResolver()
        rr = self._execute_qry(qry)
        return rr.resolve_string(self._res_key)
