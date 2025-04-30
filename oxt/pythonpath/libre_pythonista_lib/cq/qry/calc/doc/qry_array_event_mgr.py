from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.array_event_mgr import ArrayEventMgr
else:
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.array_event_mgr import ArrayEventMgr


class QryArrayEventMgr(QryBase, QryDocT[ArrayEventMgr]):
    """Gets the singleton ArrayEventMgr"""

    def __init__(self, doc: CalcDoc) -> None:
        """Constructor

        Args:
            doc (CalcDoc): The Calc document
        """
        QryBase.__init__(self)
        self._doc = doc

    def execute(self) -> ArrayEventMgr:
        """Executes the query to get the singleton ArrayEventMgr"""
        return ArrayEventMgr(doc=self._doc)
