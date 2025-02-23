from __future__ import annotations

from __future__ import annotations
from typing import List, Type, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_ctl_name import CmdCtlName
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_ctl_name import CmdCtlName
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl


class CtlBuilder(List[Type[CmdCellCtlT]], LogMixin):
    def __init__(self, cell: CalcCell) -> None:
        list.__init__(self)
        LogMixin.__init__(self)
        self.ctl = Ctl()
        self.ctl.cell = cell
        self._success = False
        self._success_cmds: List[CmdCellCtlT] = []
        self._handler = CmdHandler()

    def append_commands(self) -> None:
        self.clear()
        self.append(CmdCodeName)
        self.append(CmdCtlName)

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
                inst = cmd(self.cell, self.ctl)
                self._handler.handle(inst)
                self._success = inst.success
                if self._success:  # Only add if command was successful
                    self._success_cmds.append(inst)
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
        self.append_commands()
        self._execute()
        return self.ctl

    @property
    def cell(self) -> CalcCell:
        return self.ctl.cell

    @property
    def success(self) -> bool:
        return self._success
