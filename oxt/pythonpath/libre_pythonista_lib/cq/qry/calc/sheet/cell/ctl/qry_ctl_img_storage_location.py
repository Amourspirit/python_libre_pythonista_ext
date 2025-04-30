from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_state_rules_default import (
        QryStateRulesDefault,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_state_rules_default import QryStateRulesDefault
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryCtlStorageLocation(QryBase, LogMixin, QryCellT[Result[str, None] | Result[None, Exception]]):
    """Gets the control storage location"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_module_state(self) -> Result[ModuleStateItem, None] | Result[None, Exception]:
        """Gets the module state via query"""
        qry = QryModuleState(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_state_rules_default(self) -> StateRules:
        """Gets the state rules default via query"""
        qry = QryStateRulesDefault()
        return self._execute_qry(qry)

    def _validate_is_image(self, state: ModuleStateItem) -> bool:
        """Validates that the state is an image"""
        state_rules = self._qry_state_rules_default()
        rule = state_rules.get_matched_rule(self.cell, state.dd_data)
        if rule is None:
            return False
        return rule.rule_kind in (RuleNameKind.CELL_DATA_TYPE_CELL_IMG, RuleNameKind.CELL_DATA_TYPE_MP_FIGURE)

    def execute(self) -> Result[str, None] | Result[None, Exception]:
        """
        Executes the query to get control name

        Returns:
            Result: Success with control name or Failure with Exception
        """
        try:
            qry_state = self._qry_module_state()
            if Result.is_failure(qry_state):
                self.log.warning("Failed to get module state")
                return qry_state
            if not self._validate_is_image(qry_state.data):
                self.log.warning("Cell %s is not an image", self.cell.cell_obj)
                return Result.failure(Exception("Cell %s is not an image", self.cell.cell_obj))

            location = qry_state.data.dd_data.get("data")
            if not location:
                return Result.failure(Exception("Failed to get location for cell %s", self.cell.cell_obj))
            if not isinstance(location, str):
                return Result.failure(Exception("Location for cell %s is not a string", self.cell.cell_obj))
            if self._ctl is not None:
                self._ctl.ctl_storage_location = location
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            self.log.debug(
                "Successfully executed query for cell %s. Storage location: %s", self.cell.cell_obj, location
            )
            return Result.success(location)

        except Exception:
            return Result.failure(Exception("Failed to execute query"))

    @property
    def cell(self) -> CalcCell:
        return self._cell
