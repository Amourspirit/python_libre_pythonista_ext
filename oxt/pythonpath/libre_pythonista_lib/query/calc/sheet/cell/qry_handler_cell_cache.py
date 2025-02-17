from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache_t import QryHandlerCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.cache.mem_cache import MemCache
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache_t import QryHandlerCellCacheT
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from libre_pythonista_lib.query.qry_handler import QryHandler


class QryHandlerCellCache(QryHandlerCellCacheT):
    def handle(self, query: QryCellCacheT) -> Any:  # noqa: ANN401
        cell_cache_qry = QryCellCache(query.cell)
        query_handler = QryHandler()
        cell_cache = cast("MemCache", query_handler.handle(cell_cache_qry))
        if not cell_cache:
            return None
        if query.cache_key in cell_cache:
            return cell_cache[query.cache_key]
        result = query.execute()
        if result is None:
            return None
        cell_cache[query.cache_key] = result
        return result
