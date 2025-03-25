from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
    from libre_pythonista_lib.utils.result import Result


class CmdArrayAbility(CmdBase, LogMixin, CmdCellT):
    """Sets the array ability of the cell"""

    def __init__(self, cell: CalcCell, ability: bool) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._state = ability
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = cast(bool | None, NULL_OBJ)
        self._state_changed = False

    def _get_state(self) -> bool:
        # use method to make possible to mock for testing
        return self._state

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _get_current_state(self) -> bool | None:
        qry = QryArrayAbility(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    @override
    def execute(self) -> None:
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()
        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()

        self.success = False
        self._state_changed = False
        try:
            if self._get_state() == self._current_state:
                self.log.debug("State is already set.")
                self.success = True
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_array_ability_key, value=self._state)
            self._execute_cmd(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting Array Ability")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return
            if self._current_state is None:
                # avoid circular import
                if TYPE_CHECKING:
                    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability_del import (
                        CmdArrayAbilityDel,
                    )
                else:
                    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability_del import (
                        CmdArrayAbilityDel,
                    )
                cmd = CmdArrayAbilityDel(cell=self.cell)
            else:
                cmd = CmdCellPropSet(cell=self.cell, name=self._keys.ctl_state_key, value=self._current_state)

            self._execute_cmd(cmd)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing Array Ability")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
