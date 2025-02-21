from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING


from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.query.qry_t import QryT, TResult


class QrySheetT(QryT[TResult], Protocol):
    @property
    def sheet(self) -> CalcSheet: ...
