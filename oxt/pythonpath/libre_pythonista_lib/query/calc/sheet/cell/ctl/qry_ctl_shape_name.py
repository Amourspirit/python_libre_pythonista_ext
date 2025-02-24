from __future__ import annotations

from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_shape import QryShape
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_shape import QryShape
    from ___lo_pip___.basic_config import BasicConfig


class QryCtlShapeName(QryCellT[str]):
    """Gets the control name"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        self._cell = cell
        self._ctl = ctl
        self._kind = CalcQryKind.CELL
        self._config = BasicConfig()
        self._qry_handler = QryHandler()

    def execute(self) -> str:
        """
        Executes the query to get control name

        Returns:
            str: The control name
        """
        qry_shape = QryShape(cell=self.cell)
        name = self._qry_handler.handle(qry_shape)
        if self._ctl is not None:
            self._ctl.ctl_shape_name = name
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return name

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
