from __future__ import annotations
from typing import Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ooodev.utils.cache import MemCache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cache.cq_cache import get_cq_cache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cache.cq_cache import get_cq_cache
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    MemCache = Any


class QryCache(QryBase, LogMixin, QryT[Union[MemCache, None]]):
    """Gets the cache"""

    def __init__(self) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SIMPLE
        self.log.debug("init done")

    def execute(self) -> Union[MemCache, None]:
        """
        Executes the query and gets the cache.

        Returns:
            MemCac, None: The cache if successful, otherwise None.
        """

        try:
            return get_cq_cache()
        except Exception:
            self.log.exception("Error executing query")
        return None
