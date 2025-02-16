from __future__ import annotations
from typing import Protocol


from ooodev.calc import CalcSheet


class CmdHandlerSheetCacheT(Protocol):
    def execute(self) -> None:  # noqa: ANN401
        ...

    @property
    def sheet(self) -> CalcSheet: ...

    @property
    def cache_key(self) -> str: ...
