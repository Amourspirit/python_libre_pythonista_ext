from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.res.res_resolver import ResResolver
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.res.res_resolver import ResResolver
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryResourceResolver(QryBase, QryT[ResResolver]):
    """Gets the resource resolver"""

    def __init__(self) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.SIMPLE

    def execute(self) -> ResResolver:
        """
        Executes the query and gets the resource resolver.

        Returns:
            ResResolver: The resource resolver.
        """

        return ResResolver()  # singleton
