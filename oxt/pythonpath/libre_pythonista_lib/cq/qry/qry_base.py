from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryBase:
    """
    Base class for queries that provides access to query handlers.
    """

    def __init__(self) -> None:
        self.__kind: CalcQryKind = CalcQryKind.SIMPLE

    @property
    def kind(self) -> CalcQryKind:
        return self.__kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self.__kind = value

    def _get_qry_handler(self) -> QryHandlerT:
        """Get the query handler to execute queries"""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        else:
            from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

        return QryHandlerFactory.get_qry_handler()

    def _execute_qry(self, query: QryT[TResult]) -> TResult:
        """Execute a query using the query handler"""
        handler = self._get_qry_handler()
        return handler.handle(query)
