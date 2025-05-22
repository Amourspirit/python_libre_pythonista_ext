from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.cq.qry.qry_t import QryT, TResult


class QryHandlerNoCache(QryHandlerT):
    def handle(self, query: QryT[TResult]) -> TResult:  # noqa: ANN401
        return query.execute()
