from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING


from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_t import QrySheetT
else:
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_t import QrySheetT


class QrySheetCacheT(QrySheetT, Protocol):
    @property
    def cache_key(self) -> str: ...
