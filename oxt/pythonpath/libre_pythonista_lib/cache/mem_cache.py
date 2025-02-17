from __future__ import annotations
from typing import Any


class MemCache:
    """
    Memory Cache
    """

    # region Initialization
    def __init__(self) -> None:
        """
        Memory Cache
        """
        self._cache = {}
        self._hits = 0

    # endregion Initialization

    # region Dictionary Methods

    def clear(self) -> None:
        """
        Clear cache.
        """
        self._cache.clear()

    def get(self, key: Any) -> Any:  # noqa: ANN401
        """
        Get value by key.

        Args:
            key (Any): Any Hashable object.

        Returns:
            Any: Value or ``None`` if not found.

        Note:
            The ``get`` method is an alias for the ``__getitem__`` method.
            So you can use ``cache_inst.get(key)`` or ``cache_inst[key]`` interchangeably.
        """
        return self[key]

    def put(self, key: Any, value: Any) -> None:  # noqa: ANN401
        """
        Put value by key.

        Args:
            key (Any): Any Hashable object.
            value (Any): Any object.

        Note:
            The ``put`` method is an alias for the ``__setitem__`` method.
            So you can use ``cache_inst.put(key, value)`` or ``cache_inst[key] = value`` interchangeably.
        """
        self[key] = value

    def remove(self, key: Any) -> None:  # noqa: ANN401
        """
        Remove key.

        Args:
            key (Any): Any Hashable object.

        Note:
            The ``remove`` method is an alias for the ``__delitem__`` method.
            So you can use ``cache_inst.remove(key)`` or ``del cache_inst[key]`` interchangeably.
        """
        del self[key]

    # endregion Dictionary Methods

    # region Dunder Methods

    def __bool__(self) -> bool:
        return True

    def __getitem__(self, key: Any) -> Any:  # noqa: ANN401
        if key is None:
            raise TypeError("Key must not be None.")
        if key not in self._cache:
            return None
        self._hits += 1
        return self._cache[key]

    def __setitem__(self, key: Any, value: Any) -> None:  # noqa: ANN401
        if key is None or value is None:
            raise TypeError("Key and value must not be None.")
        self._cache[key] = value

    def __contains__(self, key: Any) -> bool:  # noqa: ANN401
        return False if key is None else key in self._cache

    def __delitem__(self, key: Any) -> None:  # noqa: ANN401
        if key is None:
            raise TypeError("Key must not be None.")
        if key in self._cache:
            del self._cache[key]

    def __repr__(self) -> str:
        return "MemCache()"

    def __str__(self) -> str:
        return "MemCache()"

    def __len__(self) -> int:
        return len(self._cache)

    # endregion Dunder Methods

    # region Properties
    @property
    def hits(self) -> int:
        """
        Hits count.

        Returns:
            int: Hits count.
        """
        return self._hits

    # endregion Properties
