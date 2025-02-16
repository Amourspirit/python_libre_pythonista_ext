from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cmd.qry_t import QryT
else:
    from libre_pythonista_lib.cmd.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.cmd.qry_t import QryT


class QryHandlerSheet(QryHandlerT):
    def handle(self, query: QryT) -> Any:  # noqa: ANN401
        return query.execute()
