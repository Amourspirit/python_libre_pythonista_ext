from __future__ import annotations


from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import SHEET_CALCULATION_EVENT
else:
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.const.cache_const import SHEET_CALCULATION_EVENT


class QrySheetCalculationEvent(LogMixin, QrySheetCacheT):
    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        self._sheet = sheet

    def execute(self) -> str | None:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        try:
            return calculate.get_sheet_calculate_event(self._sheet)
        except Exception:
            self.log.exception("Error getting script url")
        return None

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return SHEET_CALCULATION_EVENT
