from __future__ import annotations


from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    MemCache = Any


class QrySheetCache(LogMixin, QryT[MemCache | None]):
    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        self._kind = CalcQryKind.SIMPLE
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

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
