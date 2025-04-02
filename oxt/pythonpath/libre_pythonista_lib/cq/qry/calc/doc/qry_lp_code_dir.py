from __future__ import annotations
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin

    OfficeDocumentT = Any


class QryLpCodeDir(QryBase, LogMixin, QryDocT[str]):
    def __init__(self, doc: OfficeDocumentT) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cfg = BasicConfig()
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
