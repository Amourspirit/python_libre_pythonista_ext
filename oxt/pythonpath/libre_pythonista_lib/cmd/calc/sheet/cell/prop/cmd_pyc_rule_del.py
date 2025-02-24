from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.query.qry_handler import QryHandler


class CmdPycRuleDel(LogMixin, CmdCellT):
    """Deletes the pyc rule of the cell if it exists"""

    def __init__(self, cell: CalcCell) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to delete the pyc rule for.
        """
        LogMixin.__init__(self)
        self._cell = cell
        self._success = False
        self._kind = CalcCmdKind.SIMPLE
        self._cmd_handler = CmdHandler()
        self._qry_handler = QryHandler()
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = cast(str, NULL_OBJ)

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._qry_handler.handle(qry)

    def _get_current_state(self) -> str:
        qry = QryPycRule(cell=self.cell)
        return self._qry_handler.handle(qry)

    def execute(self) -> None:
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()
        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()

        self._success = False
        try:
            if not self._current_state:
                self.log.debug("Property does not exist on cell. Nothing to delete.")
                self._success = True
                return
            cmd = CmdCellPropDel(cell=self.cell, name=self._keys.pyc_rule_key)
            self._cmd_handler.handle(cmd)
        except Exception:
            self.log.exception("Error deleting cell pyc rule")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            if not self._current_state:
                self.log.debug("No Current State. Unable to undo.")
                return
            cmd = CmdPycRule(cell=self.cell, name=self._current_state)
            self._cmd_handler.handle(cmd)
            if cmd.success:
                self.log.debug("Successfully executed undo command.")
            else:
                self.log.error("Failed to execute undo command.")
        except Exception:
            self.log.exception("Error undoing cell pyc rule")

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
