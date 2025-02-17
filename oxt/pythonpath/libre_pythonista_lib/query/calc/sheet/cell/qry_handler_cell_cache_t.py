from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT


class QryHandlerCellCacheT(Protocol):
    def handle(self, query: QryCellCacheT) -> Any:  # noqa: ANN401
        ...
