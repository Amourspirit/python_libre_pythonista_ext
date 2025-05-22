from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_array_ability import (
        QryArrayAbility as QryPropArrayAbility,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_array_ability import (
        QryArrayAbility as QryPropArrayAbility,
    )
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.utils.result import Result


class QryArrayAbility(QryBase, QryCellT[Union[Result[bool, None], Result[None, Exception]]]):
    """Gets the array ability."""

    def __init__(self, cell: CalcCell, ctl: Optional[Ctl] = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL

    def execute(self) -> Union[Result[bool, None], Result[None, Exception]]:
        """
        Executes the query to get array ability.

        Returns:
            Result: Success with array ability or Failure with Exception
        """
        qry_ability = QryPropArrayAbility(cell=self.cell)
        result = self._execute_qry(qry_ability)
        if Result.is_failure(result):
            return result
        if self._ctl is not None:
            self._ctl.array_ability = result.data
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return result

    @property
    def cell(self) -> CalcCell:
        return self._cell
