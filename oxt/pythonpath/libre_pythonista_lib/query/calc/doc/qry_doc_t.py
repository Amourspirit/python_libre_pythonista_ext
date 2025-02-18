from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
else:
    from libre_pythonista_lib.query.qry_t import QryT


class QryDocT(QryT, Protocol):
    def __init__(self, doc: CalcDoc) -> None: ...
