from __future__ import annotations
from typing import Any, Protocol


from ooodev.calc import CalcSheet


class QrySheetCacheT(Protocol):
    def execute(self) -> Any:  # noqa: ANN401
        ...

    @property
    def sheet(self) -> CalcSheet: ...

    @property
    def cache_key(self) -> str: ...
