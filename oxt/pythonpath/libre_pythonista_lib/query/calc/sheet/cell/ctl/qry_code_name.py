from __future__ import annotations

from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import (
        QryCodeName as QryPropCodeName,
    )
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import QryCodeName as QryPropCodeName


class QryCodeName(QryCellT[str]):
    """Gets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        self._cell = cell
        self._ctl = ctl
        self._kind = CalcQryKind.CELL
        self._qry_handler = QryHandler()

    def execute(self) -> str:
        """
        Executes the query to get code name

        Returns:
            str: The code name
        """
        qry_code_name = QryPropCodeName(cell=self.cell)
        value = self._qry_handler.handle(qry_code_name)

        if self._ctl is not None:
            self._ctl.ctl_code_name = value
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.CELL``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
