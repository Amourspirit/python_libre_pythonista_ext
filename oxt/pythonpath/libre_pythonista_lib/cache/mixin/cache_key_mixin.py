from __future__ import annotations


class CacheKeyMixin:
    def __init__(self) -> None:
        self.__cache_key = self._get_cache_key()

    def _get_cache_key(self) -> str:
        raise NotImplementedError

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return self.__cache_key
