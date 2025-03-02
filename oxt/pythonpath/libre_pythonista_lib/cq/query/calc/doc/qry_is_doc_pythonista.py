from __future__ import annotations


from typing import TYPE_CHECKING


from ooodev.io.sfa import Sfa

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_lp_code_dir import QryLpCodeDir

else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.calc.doc.qry_lp_code_dir import QryLpCodeDir


class QryIsDocPythonista(QryBase, LogMixin, QryDocT[bool | None]):
    def __init__(self, doc: CalcDoc) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
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
        return self._execute_qry(qry)

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
