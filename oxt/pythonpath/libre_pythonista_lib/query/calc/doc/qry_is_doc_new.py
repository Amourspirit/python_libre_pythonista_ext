from __future__ import annotations


from typing import TYPE_CHECKING
from ooodev.exceptions import ex as mEx  # noqa: N812


from ooodev.utils.props import Props

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from libre_pythonista_lib.query.qry_base import QryBase
    from libre_pythonista_lib.query.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin


# this class should be call in:
# libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache.QryHandlerSheetCache
class QryIsDocNew(QryBase, LogMixin, QryDocT[bool | None]):
    def __init__(self, doc: CalcDoc) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc

    def execute(self) -> bool | None:
        """
        Executes the query to check if the document is a new unsaved document.

        Returns:
            bool | None: True if the document is new, None if there are any errors; False otherwise.
        """
        try:
            result = True
            doc_args = self._doc.component.getArgs()
            args_dic = Props.props_to_dot_dict(doc_args)
            if hasattr(args_dic, "URL"):
                result = args_dic.URL == ""
            self.log.debug("Document is new: %s", result)
            return result
        except Exception:
            self.log.exception("Error executing query")
        return None
