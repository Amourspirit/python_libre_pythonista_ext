from __future__ import annotations
from typing import TYPE_CHECKING
from ..utils.singleton import SingletonMeta

if TYPE_CHECKING:
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class ResResolver(metaclass=SingletonMeta):

    def __init__(self):
        if getattr(self, "_is_init", False):
            return
        from ooodev.loader import Lo

        ctx = Lo.get_context()
        self._rr = ResourceResolver(ctx)
        self._is_init = True

    def resolve_string(self, id: str) -> str:
        """Resolve localized string

        Args:
            id (str): resource id

        Returns:
            str: localized string
        """
        return self._rr.resolve_string(id)
