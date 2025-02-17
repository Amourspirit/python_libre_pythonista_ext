from __future__ import annotations


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.qry_t import QryT


class QrySheetCache(LogMixin, QryT):
    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        self._sheet = sheet

    def execute(self) -> MemCache | None:
        """
        Executes the query and gets the cell cache.

        Returns:
            MemCache | None: The sheet cache if successful, otherwise None.
        """

        try:
            return get_sheet_cache(self._sheet)
        except Exception:
            self.log.exception("Error executing query")
        return None
