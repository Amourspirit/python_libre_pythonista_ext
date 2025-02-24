from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from ___lo_pip___.basic_config import BasicConfig


class CmdCtlName(LogMixin, CmdCellCtlT):
    """Sets the address of the cell such as ``sheet_index=0&cell_addr=A1``"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        LogMixin.__init__(self)
        self._ctl = ctl
        self._success = False
        self._is_deleted = None
        self._config = BasicConfig()

        self._kind = CalcCmdKind.SIMPLE
        self._cmd_handler = CmdHandler()
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_state = self._ctl.ctl_name

    def execute(self) -> None:
        self._success = False
        self._state_changed = False
        if not self._ctl.ctl_code_name:
            self.log.error("Error setting cell address: ctl_code_name is empty")
            return
        try:
            control_name = f"{self._config.general_code_name}_ctl_cell_{self._ctl.ctl_code_name}"

            if self._current_state and control_name == self._current_state:
                self.log.debug("State is already set.")
                self._success = True
                return
            self._ctl.ctl_name = control_name
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell address")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        self._ctl.ctl_name = self._current_state
        self.log.debug("Successfully executed undo command.")

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
        return self._ctl.cell

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
