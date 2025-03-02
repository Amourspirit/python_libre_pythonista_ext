from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.utils.props import Props

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_office_doc_t import QryOfficeDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.doc.qry_office_doc_t import QryOfficeDocT


class QryIsMacroEnabled(QryBase, LogMixin, QryOfficeDocT[bool]):
    def __init__(self, doc: OfficeDocumentT) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc

    def execute(self) -> bool:
        """
        Executes the query to get if macros are enabled for the document.

        Returns:
            bool: True if macros are enabled, False otherwise.
        """

        try:
            doc_args = self._doc.component.getArgs()
            args_dic = Props.props_to_dot_dict(doc_args)
            macros_enabled = getattr(args_dic, "MacroExecutionMode", None) == 4
            self.log.debug("Macros enabled: %s", macros_enabled)
            return macros_enabled
        except Exception:
            self.log.exception("Error getting script url")
        return False
