from __future__ import annotations


from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_VIEW_LOADED

else:
    from libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.const.cache_const import DOC_VIEW_LOADED


# this class should be call in:
# libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache.QryHandlerSheetCache
class QryIsViewLoaded(LogMixin, QryDocT):
    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        self._kind = CalcQryKind.SIMPLE
        self._doc = doc

    def execute(self) -> bool | None:
        """
        Executes the query to check if the document view is loaded.

        Returns:
            bool: True if the document view is loaded, False otherwise.
        """
        try:
            cache = DocGlobals.get_current_mem_cache()
            result = DOC_VIEW_LOADED in cache
            self.log.debug("Document View Loaded: %s", result)
            return result
        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
