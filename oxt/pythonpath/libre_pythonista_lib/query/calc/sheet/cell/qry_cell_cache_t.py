from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT


class QryCellCacheT(QryCellT, Protocol):
    @property
    def cache_key(self) -> str: ...
