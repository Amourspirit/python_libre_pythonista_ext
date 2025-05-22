from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.result import Result


class QryCtlKind(QryBase, QryCellT[Union[Result[CtlKind, None], Result[None, Exception]]]):
    """Gets the kind of the control for the cell"""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> Union[Result[CtlKind, None], Result[None, Exception]]:
        """
        Executes the query and gets the pyc rule of the cell.

        Returns:
            Result: Success with CtlKind or Failure with Exception
        """
        qry = QryPycRule(self._cell)
        result = self._execute_qry(qry)
        if Result.is_failure(result):
            return result
        return Result.success(CtlKind.from_rule_name_kind(result.data))

    @property
    def cell(self) -> CalcCell:
        return self._cell
