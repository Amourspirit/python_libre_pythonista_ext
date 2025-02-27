from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals, MemCache
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals

    MemCache = Any

_KEY = "libre_pythonista_lib.cache.cq_cache"


def get_cq_cache() -> MemCache:
    """Get command query cache from doc globals cache"""
    doc_globals = DocGlobals.get_current()
    cache = doc_globals.get_mem_cache(DocGlobals.CacheType.GENERAL, unique_id=_KEY)
    return cache


def remove_cq_cache() -> None:
    """Remove command query cache from doc globals cache"""
    doc_globals = DocGlobals.get_current()
    doc_globals.remove_mem_cache(DocGlobals.CacheType.GENERAL, unique_id=_KEY)
