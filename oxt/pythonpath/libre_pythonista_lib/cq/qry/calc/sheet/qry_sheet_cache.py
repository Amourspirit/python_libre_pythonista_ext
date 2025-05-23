from __future__ import annotations
from typing import Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ooodev.utils.cache import MemCache
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    MemCache = Any


class QrySheetCache(QryBase, LogMixin, QrySheetT[Union[MemCache, None]]):
    def __init__(self, sheet: CalcSheet) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SHEET
        self._sheet = sheet
        self.log.debug("init done for sheet %s", sheet.name)

    def execute(self) -> Union[MemCache, None]:
        """
        Executes the query and gets the cell cache.

        Returns:
            MemCache, None: The sheet cache if successful, otherwise None.
        """

        try:
            return get_sheet_cache(self._sheet)
        except Exception:
            self.log.exception("Error executing query")
        return None

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
