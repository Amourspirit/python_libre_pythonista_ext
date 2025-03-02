from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_office_doc_t import QryOfficeDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_doc_custom_prop import QryDocCustomProp
    from oxt.pythonpath.libre_pythonista_lib.const import LP_EXT_VERSION
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.doc.qry_office_doc_t import QryOfficeDocT
    from libre_pythonista_lib.cq.query.doc.qry_doc_custom_prop import QryDocCustomProp
    from libre_pythonista_lib.const import LP_EXT_VERSION

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_version.py


class QryLpVersion(QryBase, QryOfficeDocT[str | None]):
    def __init__(self, doc: OfficeDocumentT) -> None:
        QryBase.__init__(self)
        self._doc = doc

    def _get_version(self) -> str | None:
        qry = QryDocCustomProp(doc=self._doc, name=LP_EXT_VERSION, default=None)
        return self._execute_qry(qry)

    def execute(self) -> str | None:
        """
        Executes the query and returns the lp version.

        Returns:
            str | None: The lp version if successful, otherwise None.
        """
        return self._get_version()
