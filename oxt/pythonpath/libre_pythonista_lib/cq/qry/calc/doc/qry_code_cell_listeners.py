from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
else:
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners
    from libre_pythonista_lib.cq.qry.qry_base import QryBase


class QryCodeCellListeners(QryBase, QryDocT[CodeCellListeners]):
    """Gets the singleton CodeCellListeners"""

    def __init__(self, doc: CalcDoc) -> None:
        """Constructor

        Args:
            doc (CalcDoc): The Calc document
        """
        QryBase.__init__(self)
        self._doc = doc

    def execute(self) -> CodeCellListeners:
        """Executes the query to get the singleton CodeCellListeners"""
        return CodeCellListeners(self._doc)
