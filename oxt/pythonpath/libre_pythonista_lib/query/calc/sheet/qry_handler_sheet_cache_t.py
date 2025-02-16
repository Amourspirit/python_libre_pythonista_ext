from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
else:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT


class QryHandlerSheetCacheT(Protocol):
    def handle(self, query: QrySheetCacheT) -> Any:  # noqa: ANN401
        ...
