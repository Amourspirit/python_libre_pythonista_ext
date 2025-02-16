from __future__ import annotations
from typing import Any, Protocol


class QryT(Protocol):
    def execute(self) -> Any:  # noqa: ANN401
        ...
