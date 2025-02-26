from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_addr import CmdAddr

    # from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_name import CmdCtlName
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_addr import CmdAddr

    # from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_name import CmdCtlName
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl


class CtlBuilder(List[CmdCellCtlT], LogMixin, ABC):
    def __init__(self, cell: CalcCell) -> None:
        list.__init__(self)
        LogMixin.__init__(self)
        self.ctl = Ctl()
        self.ctl.cell = cell
        self._success = False
        self._success_cmds: List[CmdCellCtlT] = []
        self._handler = CmdHandler()

    def _append_base_commands(self) -> None:
        self.clear()
        self.append(CmdCodeName(self.cell, self.ctl))
        self.append(CmdAddr(self.cell, self.ctl))
        self.append_commands()

    @abstractmethod
    def append_commands(self) -> None:
        """Appends commands to the list of commands to be executed."""
        ...

    def _execute(self) -> None:
        """
        Executes a series of commands as part of a composite command.
        This method iterates over the commands, executing each one and collecting successful commands.
        If any command fails, it logs the failure, undoes all previously executed commands, and sets the success flag to False.
        If all commands succeed, it sets the success flag to True.
        In case of an unexpected exception, it logs the exception, undoes all executed commands, and sets the success flag to False.

        Returns:
            None: This method does not return anything.
        """

        self._success = False
        try:
            for cmd in self:
                self._handler.handle(cmd)
                self._success = cmd.success
                if self._success:  # Only add if command was successful
                    self._success_cmds.append(cmd)
                else:
                    self.log.debug("A command failed. Undoing previously executed commands.")
                    break

            if not self._success:
                self.log.debug("Composite command failed.")
                self._undo()
                return
        except Exception as e:
            self.log.exception("An unexpected error occurred: %s", e)
            self._undo()
            self._success = False

        if self.success:
            self.log.debug("Successfully executed command.")

    def _undo(self) -> None:
        for cmd in reversed(self._success_cmds):
            cmd.undo()
        self._success_cmds = []  # Clear executed commands
        self._success = False  # Reset success flag.

    def build(self) -> Ctl:
        self._append_base_commands()
        self._execute()
        return self.ctl

    @property
    def cell(self) -> CalcCell:
        return self.ctl.cell

    @property
    def success(self) -> bool:
        return self._success
