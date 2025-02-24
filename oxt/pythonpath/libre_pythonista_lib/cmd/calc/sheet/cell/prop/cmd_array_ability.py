from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility


class CmdArrayAbility(LogMixin, CmdCellT):
    """Sets the array ability of the cell"""

    def __init__(self, cell: CalcCell, ability: bool) -> None:
        LogMixin.__init__(self)
        self._cell = cell
        self._success = False
        self._state = ability
        self._kind = CalcCmdKind.SIMPLE
        self._cmd_handler = CmdHandler()
        self._qry_handler = QryHandler()
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = NULL_OBJ
        self._state_changed = False

    def _get_state(self) -> bool:
        # use method to make possible to mock for testing
        return self._state

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._qry_handler.handle(qry)

    def _get_current_state(self) -> bool:
        qry = QryArrayAbility(cell=self.cell)
        return self._qry_handler.handle(qry)

    def execute(self) -> None:
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()
        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()

        self._success = False
        self._state_changed = False
        try:
            if self._get_state() == self._current_state:
                self.log.debug("State is already set.")
                self._success = True
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_array_ability_key, value=self._state)
            self._cmd_handler.handle(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting Array Ability")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.ctl_state_key, value=self._current_state)
            self._cmd_handler.handle(cmd)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing Array Ability")

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
