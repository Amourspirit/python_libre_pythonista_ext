from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache_t import QryHandlerSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache import QrySheetCache
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
else:
    from libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache_t import QryHandlerSheetCacheT
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache import QrySheetCache


class QryHandlerSheetCache(QryHandlerSheetCacheT):
    def handle(self, query: QrySheetCacheT) -> Any:  # noqa: ANN401
        cache_qry = QrySheetCache(query.sheet)
        cache = cast("MemCache", QryHandler().handle(cache_qry))
        if not cache:
            return None
        if query.cache_key in cache:
            return cache[query.cache_key]
        result = query.execute()
        if result is None:
            return None
        cache[query.cache_key] = result
        return result
