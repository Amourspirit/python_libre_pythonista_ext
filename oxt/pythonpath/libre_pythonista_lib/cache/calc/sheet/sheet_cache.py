from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from ooodev.utils.cache import MemCache
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals

    MemCache = Any


def get_sheet_cache(sheet: CalcSheet) -> MemCache:
    """Get cache sheet from cache"""
    doc_globals = DocGlobals.get_current(uid=sheet.calc_doc.runtime_uid)
    cache = doc_globals.get_mem_cache(DocGlobals.CacheType.CALC_DOC, unique_id=sheet.unique_id)
    return cache


def remove_sheet_cache(sheet: CalcSheet) -> None:
    """Remove cache sheet from cache"""
    doc_globals = DocGlobals.get_current(uid=sheet.calc_doc.runtime_uid)
    doc_globals.remove_mem_cache(DocGlobals.CacheType.CALC_DOC, unique_id=sheet.unique_id)
