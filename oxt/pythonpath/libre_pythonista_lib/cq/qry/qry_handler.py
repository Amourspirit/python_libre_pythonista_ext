from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.utils.cache import MemCache
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_cache import QryCache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache import QryCellCache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache import QrySheetCache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_managed_cache_t import QrySheetManagedCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache_mgr import SheetCacheMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.qry.general.qry_cache import QryCache
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache import QryCellCache
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache import QrySheetCache
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_managed_cache_t import QrySheetManagedCacheT
    from libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache_mgr import SheetCacheMgr
    from libre_pythonista_lib.cq.qry.qry_t import QryT, TResult

    MemCache = Any


class QryHandler(QryHandlerT):
    def handle(self, query: QryT[TResult]) -> TResult:  # noqa: ANN401
        if query.kind in (CalcQryKind.SIMPLE, CalcQryKind.CELL, CalcQryKind.SHEET):
            return self._handle_simple(query)
        elif query.kind == CalcQryKind.SIMPLE_CACHE:
            return cast(TResult, self._handle_simple_cache(cast(QryCacheT, query)))
        elif query.kind == CalcQryKind.CELL_CACHE:
            return cast(TResult, self._handle_cell_cache(cast(QryCellCacheT, query)))
        elif query.kind == CalcQryKind.SHEET_CACHE:
            return cast(TResult, self._handle_sheet_cache(cast(QrySheetCacheT, query)))
        elif query.kind == CalcQryKind.SHEET_MANAGED_CACHE:
            return cast(TResult, self._handle_sheet_managed_cache(cast(QrySheetManagedCacheT, query)))
        else:
            raise NotImplementedError

    def _handle_simple(self, query: QryT[TResult]) -> TResult:  # noqa: ANN401
        return query.execute()

    def _handle_simple_cache(self, query: QryCacheT) -> object:  # noqa: ANN401
        cache_qry = QryCache()
        cache = cast(MemCache, self._handle_simple(cache_qry))
        if not cache:
            return None
        if query.cache_key in cache:
            return cache[query.cache_key]
        result = query.execute()
        # if result is None:
        #     return None
        cache[query.cache_key] = result
        return result

    def _handle_cell_cache(self, query: QryCellCacheT) -> object:  # noqa: ANN401
        cache_qry = QryCellCache(query.cell)
        cache = cast(MemCache, self._handle_simple(cache_qry))
        if not cache:
            return None
        if query.cache_key in cache:
            return cache[query.cache_key]
        result = query.execute()
        # if result is None:
        #     return None
        cache[query.cache_key] = result
        return result

    def _handle_sheet_cache(self, query: QrySheetCacheT) -> object:  # noqa: ANN401
        cache_qry = QrySheetCache(query.sheet)
        cache = cast(MemCache, self._handle_simple(cache_qry))
        if not cache:
            return None
        if query.cache_key in cache:
            return cache[query.cache_key]
        result = query.execute()
        # if result is None:
        #     return None
        cache[query.cache_key] = result
        return result

    def _handle_sheet_managed_cache(self, query: QrySheetManagedCacheT) -> object:  # noqa: ANN401
        """Handle sheet managed cache query"""

        # see cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet.QryLpCellsBySheet

        # The sheet_cache_mgr is a singleton.
        # It registers keys with event names.
        # When those events are triggered the key is removed from the sheet cache.
        sheet_cache_mgr = SheetCacheMgr(query.sheet)
        key, event_names = query.cache_key_events
        cache = sheet_cache_mgr.sheet_cache
        if not cache:
            return None
        if key in cache:
            return cache[key]
        result = query.execute()
        for event_name in event_names:
            sheet_cache_mgr.register_key(key, event_name)
        cache[key] = result
        return result
