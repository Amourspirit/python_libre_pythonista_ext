from __future__ import annotations
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cache.mem_cache import MemCache
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.qry_sheet_cache import QrySheetCache
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from libre_pythonista_lib.cq.query.calc.sheet.qry_sheet_cache import QrySheetCache
    from libre_pythonista_lib.cq.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.cq.query.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.cq.query.qry_t import QryT, TResult


class QryHandler(QryHandlerT):
    def handle(self, query: QryT[TResult]) -> TResult:  # noqa: ANN401
        if query.kind in (CalcQryKind.SIMPLE, CalcQryKind.CELL, CalcQryKind.SHEET):
            return self._handle_simple(query)
        elif query.kind == CalcQryKind.CELL_CACHE:
            return cast(TResult, self._handle_cell_cache(cast(QryCellCacheT, query)))
        elif query.kind == CalcQryKind.SHEET_CACHE:
            return cast(TResult, self._handle_sheet_cache(cast(QrySheetCacheT, query)))
        else:
            raise NotImplementedError

    def _handle_simple(self, query: QryT[TResult]) -> TResult:  # noqa: ANN401
        return query.execute()

    def _handle_cell_cache(self, query: QryCellCacheT) -> object:  # noqa: ANN401
        cell_cache_qry = QryCellCache(query.cell)
        cell_cache = cast("MemCache", self._handle_simple(cell_cache_qry))
        if not cell_cache:
            return None
        if query.cache_key in cell_cache:
            return cell_cache[query.cache_key]
        result = query.execute()
        if result is None:
            return None
        cell_cache[query.cache_key] = result
        return result

    def _handle_sheet_cache(self, query: QrySheetCacheT) -> object:  # noqa: ANN401
        cache_qry = QrySheetCache(query.sheet)
        cache = cast("MemCache", self._handle_simple(cache_qry))
        if not cache:
            return None
        if query.cache_key in cache:
            return cache[query.cache_key]
        result = query.execute()
        if result is None:
            return None
        cache[query.cache_key] = result
        return result
