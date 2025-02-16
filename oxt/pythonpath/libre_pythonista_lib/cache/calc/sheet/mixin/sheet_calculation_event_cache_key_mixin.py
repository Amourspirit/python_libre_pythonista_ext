from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cache.mixin.cache_key_mixin import CacheKeyMixin
else:
    from libre_pythonista_lib.cache.mixin.cache_key_mixin import CacheKeyMixin


class SheetCalculationEventCacheKeyMixin(CacheKeyMixin):
    def _get_cache_key(self) -> str:
        return "SheetCalculationEventCacheKey"
