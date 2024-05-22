from __future__ import annotations
from typing import Any
from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class ResResolver:

    _instance = None

    def __new__(cls, ctx: Any, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ResResolver, cls).__new__(cls, *args, **kwargs)
            cls._instance._is_initialized = False
        return cls._instance

    def __init__(self, ctx):
        if self._is_initialized:
            return
        # from ___lo_pip___.lo_util.resource_resolver import ResourceResolver

        self._ctx = ctx
        self._rr = ResourceResolver(ctx)
        self._is_initialized = True

    def resolve_string(self, id: str) -> str:
        """Resolve localized string

        Args:
            id (str): resource id

        Returns:
            str: localized string
        """
        return self._rr.resolve_string(id)

    @property
    def ctx(self) -> Any:
        return self._ctx
