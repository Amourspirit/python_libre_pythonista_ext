from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_modify_trigger_event import (
        QryModifyTriggerEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_modify_trigger_event import QryModifyTriggerEvent
    from libre_pythonista_lib.utils.result import Result


class QryCtlModifyTriggerEvent(QryBase, LogMixin, QryCellT[Union[Result[str, None], Result[None, Exception]]]):
    """
    Gets the modify trigger event of the cell such as ``cell_data_type_str``.

    Assigns the modify trigger event to the control as property ``modify_trigger_event``.
    """

    def __init__(self, cell: CalcCell, ctl: Optional[Ctl] = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL
        self.log.debug("init done for cell %s", cell.cell_obj)

    def execute(self) -> Union[Result[str, None], Result[None, Exception]]:
        """
        Executes the query to get the modify trigger event of the cell.

        Assigns the modify trigger event to the control as property ``modify_trigger_event``

        Returns:
            Result: Success with modify trigger event or Failure with Exception
        """
        qry_shape = QryModifyTriggerEvent(cell=self.cell)
        result = self._execute_qry(qry_shape)
        if Result.is_failure(result):
            return result
        if self._ctl is not None:
            try:
                kind = RuleNameKind(result.data)
                self._ctl.modify_trigger_event = kind
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            except Exception:
                self.log.exception("Error getting rule name")
        return result

    @property
    def cell(self) -> CalcCell:
        return self._cell
