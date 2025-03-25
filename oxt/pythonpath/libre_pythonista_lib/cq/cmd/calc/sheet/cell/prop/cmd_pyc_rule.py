from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.utils.result import Result


class CmdPycRule(CmdBase, LogMixin, CmdCellT):
    """Sets the pyc rule of the cell such as ``cell_data_type_str``"""

    def __init__(self, cell: CalcCell, name: str | RuleNameKind) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the pyc rule for.
            name (str, RuleNameKind): Pyc Rule name to set such as ``cell_data_type_str`` or ``RuleNameKind.CELL_DATA_TYPE_STR``.
                Cannot be empty.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.kind = CalcCmdKind.CELL
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = cast(str | None, NULL_OBJ)
        self._state_changed = False
        self._errors = True
        rule_name = str(name)
        if not rule_name:
            self.log.error("Error setting pyc rule: name is empty")
            return
        if rule_name == RuleNameKind.UNKNOWN.value:
            self.log.error("Error setting pyc rule: name is UNKNOWN")
            return

        self._state = rule_name
        self._errors = False

    def _get_state(self) -> str:
        # use method to make possible to mock for testing
        return self._state

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _get_current_state(self) -> RuleNameKind:
        qry = QryPycRule(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return RuleNameKind.UNKNOWN

    @override
    def execute(self) -> None:
        self.success = False
        if self._errors:
            self.log.error("Errors occurred during initialization. Unable to execute command.")
            return

        if self._current_state is NULL_OBJ:
            cs = self._get_current_state()
            if cs == RuleNameKind.UNKNOWN:
                self._current_state = None
            else:
                self._current_state = str(cs)

        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()

        self._state_changed = False
        try:
            if self._current_state and self._get_state() == self._current_state:
                self.log.debug("State is already set.")
                self.success = True
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.pyc_rule_key, value=self._state)
            self._execute_cmd(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell pyc rule")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return

            if self._current_state:
                cmd = CmdCellPropSet(cell=self.cell, name=self._keys.pyc_rule_key, value=self._current_state)

            else:
                if TYPE_CHECKING:
                    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule_del import (
                        CmdPycRuleDel,
                    )
                else:
                    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule_del import CmdPycRuleDel
                cmd = CmdPycRuleDel(cell=self.cell)

            self._execute_cmd(cmd)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell pyc rule")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
