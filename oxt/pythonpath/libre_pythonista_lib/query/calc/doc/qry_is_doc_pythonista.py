from __future__ import annotations


from typing import TYPE_CHECKING
from ooodev.exceptions import ex as mEx  # noqa: N812


from ooodev.utils.props import Props
from ooodev.io.sfa import Sfa

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_lp_code_dir import QryLpCodeDir
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler

else:
    from libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.query.calc.doc.qry_lp_code_dir import QryLpCodeDir
    from libre_pythonista_lib.query.qry_handler import QryHandler


# this class should be call in:
# libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache.QryHandlerSheetCache
class QryIsDocPythonista(LogMixin, QryDocT[bool | None]):
    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        self._kind = CalcQryKind.SIMPLE
        self._doc = doc
        self._sfa = Sfa()

    def _get_lp_code_dir(self) -> str:
        """
        Gets the lp code directory.

        Returns:
            str: Dir for code something like ``vnd.sun.star.tdoc:/1/librepythonista``.
                If there is an error, an empty string is returned.
        """
        qry = QryLpCodeDir(self._doc)
        handler = QryHandler()
        return handler.handle(qry)

    def execute(self) -> bool | None:
        """
        Executes the query to check if the document is a LibrePythonista document.

        Returns:
            bool | None: True if the document is LibrePythonista, None if there are any errors; False otherwise.
        """
        try:
            lp_code_dir = self._get_lp_code_dir()
            if lp_code_dir == "":
                return None
            result = self._sfa.exists(lp_code_dir)
            self.log.debug("is LibrePythonista doc: %s", result)
            return result
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
