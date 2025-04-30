from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_cache import CellCache
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_cache import CellCache
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QryCellCache(QryBase, LogMixin, QryDocT[CellCache]):
    """Gets the singleton CellCache"""

    def __init__(self, doc: CalcDoc) -> None:
        """Constructor

        Args:
            doc (CalcDoc): The Calc document
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def execute(self) -> CellCache:
        """Executes the query to get the singleton CellCache"""
        return CellCache(doc=self._doc)
