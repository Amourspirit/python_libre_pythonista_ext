from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_office_doc_t import QryOfficeDocT
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.doc.qry_office_doc_t import QryOfficeDocT
    from libre_pythonista.basic_config import BasicConfig

# tested in: tests/test_cmd/test_cmd_py_src.py


class QryLpRootUri(QryBase, QryOfficeDocT[str]):
    def __init__(self, doc: OfficeDocumentT) -> None:
        QryBase.__init__(self)
        self._doc = doc
        self._config = BasicConfig()

    def execute(self) -> str:
        """
        Executes the query and returns the lp root uri.
        In format ``vnd.sun.star.tdoc:/1/librepythonista``

        Returns:
            str: The lp root uri.
        """
        return f"vnd.sun.star.tdoc:/{self._doc.runtime_uid}/{self._config.lp_code_dir}"
