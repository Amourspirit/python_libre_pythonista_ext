from __future__ import annotations
from typing import Any, cast, Union

from com.sun.star.lang import XMultiComponentFactory


class DialogBase:
    """Base class for dialog."""

    def __init__(self, ctx: Any):
        self.ctx = ctx
        self.service_manager = cast(XMultiComponentFactory, ctx.getServiceManager())

    def create(self, name: str, arguments: Union[tuple, None] = None) -> Any:
        """Create service instance."""
        if arguments:
            return self.service_manager.createInstanceWithArgumentsAndContext(name, arguments, self.ctx)
        else:
            return self.service_manager.createInstanceWithContext(name, self.ctx)
