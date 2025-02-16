from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache_t import QryHandlerSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
else:
    from libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache_t import QryHandlerSheetCacheT
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache


class QryHandlerSheetCache(QryHandlerSheetCacheT):
    def handle(self, query: QrySheetCacheT) -> Any:  # noqa: ANN401
        cache = get_sheet_cache(query.sheet)
        if query.cache_key in cache:
            return cache[query.cache_key]
        result = query.execute()
        cache[query.cache_key] = result
        return result
