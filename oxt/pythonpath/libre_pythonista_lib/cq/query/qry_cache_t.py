from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import TResult
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT
else:
    from libre_pythonista_lib.cq.query.qry_t import TResult
    from libre_pythonista_lib.cq.query.qry_t import QryT


class QryCacheT(QryT[TResult], Protocol):
    @property
    def cache_key(self) -> str: ...
