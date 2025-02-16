from __future__ import annotations
from typing import Protocol


class CmdT(Protocol):
    def execute(self) -> None:  # noqa: ANN401
        ...

    def undo(self) -> None:  # noqa: ANN401
        ...

    @property
    def success(self) -> bool: ...
