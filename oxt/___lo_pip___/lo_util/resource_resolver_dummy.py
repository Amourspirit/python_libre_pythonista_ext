from __future__ import annotations
from typing import Any


class ResourceResolverDummy:
    """Resource Resolver for localized strings"""

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        pass

    def resolve_string(self, id: str) -> str:
        """Resolve localized string

        Args:
            id (str): resource id

        Returns:
            str: localized string
        """
        return id
