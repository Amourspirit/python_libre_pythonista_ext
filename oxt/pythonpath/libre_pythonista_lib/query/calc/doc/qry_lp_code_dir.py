from __future__ import annotations


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.___lo_pip___.basic_config import BasicConfig

else:
    from libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from ___lo_pip___.basic_config import BasicConfig


# this class should be call in:
# libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache.QryHandlerSheetCache
class QryLpCodeDir(LogMixin, QryDocT):
    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        self._cfg = BasicConfig()
        self._kind = CalcQryKind.SIMPLE
        self._doc = doc

    def execute(self) -> str:
        """
        Executes the query and returns the lp code directory.

        Returns:
            str: Dir for code something like ``vnd.sun.star.tdoc:/1/librepythonista``.
                If there is an error, an empty string is returned.
        """
        try:
            result = f"vnd.sun.star.tdoc:/{self._doc.runtime_uid}/{self._cfg.lp_code_dir}"
            self.log.debug("LpCodeDir is: %s", result)
            return result
        except Exception:
            self.log.exception("Error executing query")
        return ""

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
