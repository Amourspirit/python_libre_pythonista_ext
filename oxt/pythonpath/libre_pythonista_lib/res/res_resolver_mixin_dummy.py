from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ....___lo_pip___.lo_util.resource_resolver_dummy import ResourceResolverDummy as ResourceResolver
else:
    from ___lo_pip___.lo_util.resource_resolver_dummy import ResourceResolverDummy as ResourceResolver


class ResResolverMixinDummy:
    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
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
