from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, Tuple


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import TResult
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
else:
    from libre_pythonista_lib.cq.qry.qry_t import TResult
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT


class QrySheetManagedCacheT(QrySheetT[TResult], Protocol):
    @property
    def cache_key_events(self) -> Tuple[str, Tuple[str, ...]]:
        """Gets the cache key and event names."""
        ...
