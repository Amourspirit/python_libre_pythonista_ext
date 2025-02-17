from __future__ import annotations
from typing import Tuple, Protocol


from ooodev.calc import CalcCell


class CmdCellCacheT(Protocol):
    def execute(self) -> None:  # noqa: ANN401
        ...

    def undo(self) -> None:  # noqa: ANN401
        ...

    @property
    def success(self) -> bool: ...

    @property
    def cell(self) -> CalcCell: ...

    @property
    def cache_keys(self) -> Tuple[str, ...]: ...
