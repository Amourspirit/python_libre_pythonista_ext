from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.sheet_event_mgr import SheetEventMgr
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.doc.calc.doc.sheet.sheet_event_mgr import SheetEventMgr


class QrySheetEventMgr(QryBase, QryT[SheetEventMgr]):
    """
    Query that returns a SheetEventMgr instance for a given CalcSheet.
    Inherits from QryBase and QryT with SheetEventMgr as the type parameter.
    """

    def __init__(self, sheet: CalcSheet) -> None:
        """
        Initialize the query with a CalcSheet instance.

        Args:
            sheet (CalcSheet): The sheet to create an event manager for
        """
        QryBase.__init__(self)
        self._sheet = sheet

    def execute(self) -> SheetEventMgr:
        """
        Execute the query by creating and returning a new SheetEventMgr.

        Returns:
            SheetEventMgr: A new sheet event manager instance for the stored sheet
        """
        return SheetEventMgr(self._sheet)
