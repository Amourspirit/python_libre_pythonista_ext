from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from com.sun.star.sheet import SheetCell  # service
else:
    from libre_pythonista_lib.query.qry_t import QryT

    SheetCell = Any


class QryUnoCellT(QryT, Protocol):
    def __init__(self, cell: SheetCell) -> None: ...
    @property
    def cell(self) -> SheetCell: ...
