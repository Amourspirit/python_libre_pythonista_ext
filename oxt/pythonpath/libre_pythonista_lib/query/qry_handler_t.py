from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
else:
    from libre_pythonista_lib.query.qry_t import QryT


class QryHandlerT(Protocol):
    def handle(self, query: QryT) -> Any:  # noqa: ANN401
        ...
