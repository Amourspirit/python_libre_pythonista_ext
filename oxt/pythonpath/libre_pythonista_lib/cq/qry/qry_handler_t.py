from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.cq.qry.qry_t import QryT, TResult


class QryHandlerT(Protocol):
    def handle(self, query: QryT[TResult]) -> TResult:  # noqa: ANN401
        ...
