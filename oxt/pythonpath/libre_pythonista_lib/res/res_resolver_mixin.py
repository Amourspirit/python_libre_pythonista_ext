from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from com.sun.star.uno import XComponentContext
else:
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class ResResolverMixin:
    def __init__(self, ctx: XComponentContext) -> None:
        """
        Constructor

        Args:
            ctx (XComponentContext): Component context
        """
        self.__rr = ResourceResolver(ctx)

    def resolve_string(self, id: str) -> str:
        """Resolve localized string

        Args:
            id (str): resource id

        Returns:
            str: localized string
        """
        return self.__rr.resolve_string(id)

    @property
    def resource_resolver(self) -> ResourceResolver:
        return self.__rr
