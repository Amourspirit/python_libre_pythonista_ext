from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_state import QryState
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache
    from oxt.pythonpath.libre_pythonista_lib.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state import CmdState
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_state import QryState
    from libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache
    from libre_pythonista_lib.cell.state.state_kind import StateKind
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_state import CmdState


class CmdStateDel(LogMixin, CmdCellT):
    """Deletes the state of the cell if it exists"""

    def __init__(self, cell: CalcCell) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to delete the state for.
        """
        LogMixin.__init__(self)
        self._cell = cell
        self._success = False
        self._kind = CalcCmdKind.SIMPLE
        self._cmd_handler = CmdHandler()
        self._qry_handler = QryHandlerNoCache()
        self._keys = self._get_keys()
        self._current_state = self._get_current_state()

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._qry_handler.handle(qry)

    def _get_current_state(self) -> StateKind:
        qry = QryState(cell=self.cell)
        return self._qry_handler.handle(qry)

    def execute(self) -> None:
        self._success = False
        try:
            if self._current_state == StateKind.UNKNOWN:
                self.log.debug("Property does not exist on cell. Nothing to delete.")
                self._success = True
                return
            cmd = CmdCellPropDel(cell=self.cell, name=self._keys.ctl_state_key)
            self._cmd_handler.handle(cmd)
        except Exception:
            self.log.exception("Error deleting cell state")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            if self._current_state == StateKind.UNKNOWN:
                self.log.debug("No Current State. Unable to undo.")
                return
            cmd = CmdState(cell=self.cell, state=self._current_state)
            self._cmd_handler.handle(cmd)
            if cmd.success:
                self.log.debug("Successfully executed undo command.")
            else:
                self.log.error("Failed to execute undo command.")
        except Exception:
            self.log.exception("Error undoing cell state")

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
