from __future__ import annotations
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_state_rules_default import (
        QryStateRulesDefault,
    )
else:
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.code.py_module_t import PyModuleT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_state_rules_default import QryStateRulesDefault
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result


class CmdRefreshControl(CmdBase, LogMixin, CmdCellT):
    """
    Command to refresh/update a cell's control based on its current state.

    This command handles creating, removing and updating controls attached to cells
    based on the cell's current Python code and state rules.

    Args:
        cell (CalcCell): The cell to refresh the control for
        mod (PyModuleT | None): Optional Python module. If None, will be queried
        force_refresh (bool): If True, forces control refresh even if same type
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None, force_refresh: bool = False) -> None:
        """
        Initialize the command with a cell, optional module and force refresh flag.

        Args:
            cell (CalcCell): The cell to refresh the control for
            mod (PyModuleT | None, optional): Optional Python module. If None, will be queried
            force_refresh (bool, optional): If True, forces control refresh even if same type. Defaults to False.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._force_refresh = force_refresh
        self._state_changed = False
        self._current_control = cast(CtlKind, None)

    def _qry_mod(self) -> PyModuleT:
        """Gets the default Python module via query"""
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def _qry_state_rules(self) -> StateRules:
        """Gets the cached state rules via query"""
        # QryStateRulesDefault is a cached query
        qry = QryStateRulesDefault()
        return self._execute_qry(qry)

    def _qry_module_state(self) -> ModuleStateItem:
        """
        Gets the module state for the cell.

        Raises:
            Exception: If query fails to get module state
        """
        if self._mod is None:
            self._mod = self._qry_mod()

        qry = QryModuleState(cell=self.cell, mod=self._mod)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_state_rule_kind(self) -> RuleNameKind:
        """Gets the rule kind that matches the cell's current state"""
        state_rules = self._qry_state_rules()
        state = self._qry_module_state()
        rule = state_rules.get_matched_rule(self.cell, state.dd_data)
        if rule is None:
            return RuleNameKind.UNKNOWN
        return rule.rule_kind

    def _qry_ctl_kind(self) -> CtlKind:
        """Gets the kind of control currently attached to the cell"""
        qry = QryCtlKind(self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return CtlKind.UNKNOWN

    def _get_control_kind(self) -> CtlKind:
        """Determines the appropriate control kind based on cell's Python code"""
        rule_kind = self._qry_state_rule_kind()
        return CtlKind.from_rule_name_kind(rule_kind)

    def execute(self) -> None:
        """
        Executes the control refresh command.

        Creates, removes or updates the cell's control based on its current state.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False

        try:
            if self._mod is None:
                self._mod = self._qry_mod()

            ctl_kind = self._get_control_kind()

            if ctl_kind == CtlKind.UNKNOWN:
                self.log.warning("Control kind is unknown. Nothing to update.")
                return

            if self._current_control is None:
                self._current_control = self._qry_ctl_kind()

            is_same_control = ctl_kind == self._current_control

            if is_same_control and not self._force_refresh:
                self.log.debug("Current Control is already the correct control. Nothing to update.")
                self.success = True
                return

            if self._current_control != CtlKind.UNKNOWN:
                ctl_director.remove_control(self.cell)
                self.log.debug("Current Control removed of type: %s", self._current_control)

            self.log.debug("Creating new control of type: %s", ctl_kind)
            _ = ctl_director.create_control(self.cell, ctl_kind)
            self.log.debug("New Control created for type: %s", ctl_kind)

            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell address")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal undo implementation that restores the previous control state.
        """
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return

            if self._current_control == CtlKind.UNKNOWN:
                self.log.warning("Current control is Unknown. Nothing to undo.")
                return

            ctl_director.remove_control(self.cell)
            ctl_director.create_control(calc_cell=self.cell, ctl_kind=self._current_control)
            self._current_control = cast(CtlKind, None)
            self._state_changed = False
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell address")

    def undo(self) -> None:
        """
        Public undo method that only executes if the command was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """Gets the cell this command operates on"""
        return self._cell
