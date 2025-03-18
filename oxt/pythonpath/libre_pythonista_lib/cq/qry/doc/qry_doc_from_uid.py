from __future__ import annotations


from typing import Any, cast, TYPE_CHECKING
from ooodev.loader import Lo
from ooodev.utils.factory.doc_factory import doc_factory


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT

    OfficeDocumentT = Any

# tested in: tests/test_cmd_qry/test_doc/test_qry_doc_from_uid.py


class QryDocFromUid(QryBase, LogMixin, QryT[OfficeDocumentT | None]):
    """
    Query to find a LibreOffice document by its RuntimeUID.

    Args:
        uid (str): The RuntimeUID of the document to find.
    """

    def __init__(self, uid: str) -> None:
        """Constructor

        Args:
            uid (str): The RuntimeUID of the document to find.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._uid = uid

    def execute(self) -> OfficeDocumentT | None:
        """
        Executes the query to find a document with the specified RuntimeUID.

        First checks the current active document, then searches through all open documents.

        Returns:
            OfficeDocumentT | None: The found document wrapped in a document factory instance,
                or None if no matching document is found or an error occurs.
        """
        try:
            desktop = Lo.current_lo.desktop
            doc = cast(Any, desktop.get_current_component())
            if doc is not None and hasattr(doc, "RuntimeUID"):
                self.log.debug("Doc has RuntimeUID")
                if doc.RuntimeUID == self._uid:
                    self.log.debug("Found current doc with RuntimeUID")
                    return doc_factory(doc=doc, lo_inst=Lo.current_lo)
            for comp in desktop.components:
                if hasattr(comp, "RuntimeUID") and comp.RuntimeUID == self._uid:
                    self.log.debug("Found doc with RuntimeUID in components")
                    return doc_factory(doc=comp, lo_inst=Lo.current_lo)
            self.log.debug("Doc not found")

        except Exception as e:
            self.log.exception("Error getting script url: %s", e)
        return None
