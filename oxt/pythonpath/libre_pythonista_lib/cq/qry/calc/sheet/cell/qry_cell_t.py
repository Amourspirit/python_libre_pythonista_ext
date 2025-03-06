from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.cq.qry.qry_t import QryT, TResult


class QryCellT(QryT[TResult], Protocol):
    @property
    def cell(self) -> CalcCell: ...
