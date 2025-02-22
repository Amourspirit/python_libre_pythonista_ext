from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache
    from libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache


class CmdPycRule(LogMixin, CmdCellT):
    """Sets the pyc rule of the cell such as ``cell_data_type_str``"""

    def __init__(self, cell: CalcCell, name: str) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the pyc rule for.
            name (str): Pyc Rule name to set such as ``cell_data_type_str``. Cannot be empty.
        """
        LogMixin.__init__(self)
        self._cell = cell
        self._success = False

        self._kind = CalcCmdKind.SIMPLE
        self._cmd_handler = CmdHandler()
        self._qry_handler = QryHandlerNoCache()
        self._keys = self._get_keys()
        self._state_changed = False
        self._errors = True
        if not name:
            self.log.error("Error setting pyc rule: name is empty")
            return
        self._state = name
        self._current_state = self._get_current_state()
        self._errors = False

    def _get_state(self) -> str:
        # use method to make possible to mock for testing
        return self._state

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._qry_handler.handle(qry)

    def _get_current_state(self) -> str:
        qry = QryPycRule(cell=self.cell)
        return self._qry_handler.handle(qry)

    def execute(self) -> None:
        self._success = False
        if self._errors:
            self.log.error("Errors occurred during initialization. Unable to execute command.")
            return
        self._state_changed = False
        try:
            if self._current_state and self._get_state() == self._current_state:
                self.log.debug("State is already set.")
                self._success = True
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.pyc_rule_key, value=self._state)
            self._cmd_handler.handle(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell pyc rule")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return
            if not self._current_state:
                self.log.debug("No Current State. Unable to undo.")
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.pyc_rule_key, value=self._current_state)
            self._cmd_handler.handle(cmd)
            self.log.debug("Successfully executed undo command.")
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
