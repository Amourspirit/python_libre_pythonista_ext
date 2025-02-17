from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING


from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
else:
    from libre_pythonista_lib.query.qry_t import QryT


class QrySheetT(QryT, Protocol):
    @property
    def sheet(self) -> CalcSheet: ...
