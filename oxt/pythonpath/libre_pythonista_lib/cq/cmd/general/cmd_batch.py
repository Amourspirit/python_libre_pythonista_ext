from __future__ import annotations
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT


class CmdBatch(CmdBase, List[CmdT], LogMixin, CmdT):
    """
    Batch Composite command for executing multiple commands in a batch. It is used to group multiple commands together and execute them as a single unit.
    """

    def __init__(self, *command: CmdT) -> None:
        """
        Initializes a composite command for executing multiple commands in a batch.

        Args:
            *command (CmdT): Variable number of commands to be executed as part of the composite command.
        """
        CmdBase.__init__(self)
        list.__init__(self)
        LogMixin.__init__(self)
        if command:
            self.extend(command)
        self._success_cmds: List[CmdT] = []

    @override
    def execute(self) -> None:
        """
        Executes a series of commands as part of a composite command.
        It iterates over the commands, executing each one and collecting successful commands.
        If any command fails, it logs the failure, undoes all previously executed commands, and sets the success flag to False.
        If all commands succeed, it sets the success flag to True.
        In case of an unexpected exception, it logs the exception, undoes all executed commands, and sets the success flag to False.

        Returns:
            None: This method does not return anything.
        """

        self.success = False
        self._success_cmds.clear()
        try:
            for cmd in self:
                self._execute_cmd(cmd)
                self.success = cmd.success
                if self.success:  # Only add if command was successful
                    self._success_cmds.append(cmd)
                else:
                    self.log.debug("A command failed. Undoing previously executed commands.")
                    break

            if not self.success:
                self.log.debug("Batch command failed.")
                self._undo()
                return
        except Exception as e:
            self.log.exception("An unexpected error occurred: %s", e)
            self._undo()
            self.success = False

        if self.success:
            self.log.debug("Successfully executed command.")

    def _undo(self) -> None:
        for cmd in reversed(self._success_cmds):
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()
        self.success = False  # Reset success flag.

    def undo(self) -> None:
        """
        Reverses the execution of all previously executed commands.
        This method iterates over the list of executed commands in reverse order,
        calling the `undo` method on each command to revert its effects. After
        all commands have been undone, the list of executed commands is cleared,
        and the success flag is reset. Additionally, the memory cache for the
        current document's global state is updated.

        Returns:
            None: This method does not return anything.
        """
        if self._success_cmds:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    def redo(self) -> None:
        """
        Re-executes all previously executed commands.
        This method iterates over the list of executed commands,
        calling the `execute` method on each command to reapply its effects.
        If any command fails, it logs the failure and sets the success flag to False.
        If all commands succeed, it sets the success flag to True.

        Returns:
            None: This method does not return anything.
        """
        if self.success:
            try:
                self._success_cmds.clear()
                for cmd in self:
                    self._execute_cmd_redo(cmd)
                    self.success = cmd.success
                    if self.success:  # Only add if command was successful
                        self._success_cmds.append(cmd)
                    else:
                        self.log.debug("A command failed. Undoing previously redone commands.")
                        break

                    if not self.success:
                        self.log.debug("Batch command failed.")
                        self._undo()
                        return
            except Exception as e:
                self.log.exception("An unexpected error occurred: %s", e)
                self._undo()
                self.success = False

        else:
            self.log.debug("Redo not needed.")
