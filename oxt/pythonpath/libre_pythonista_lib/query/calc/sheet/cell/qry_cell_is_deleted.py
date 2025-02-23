from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import (
        QryCellIsDeleted as UnoQryCellIsDeleted,
    )
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import (
        QryCellIsDeleted as UnoQryCellIsDeleted,
    )
    from libre_pythonista_lib.query.qry_handler import QryHandler


class QryCellIsDeleted(QryCellT[bool]):
    """Gets the source code for a cell"""

    def __init__(self, cell: CalcCell) -> None:
        """Constructor

        Args:
            uri (str): URI of the source code.
            cell (CalcCell): Cell to query.
            src_provider (PySrcProvider, optional): Source provider. Defaults to None.
        """
        self._cell = cell
        self._kind = CalcQryKind.SIMPLE

    def execute(self) -> bool:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        qh = QryHandler()
        qry = UnoQryCellIsDeleted(cell=self._cell.component)
        return qh.handle(qry)

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
