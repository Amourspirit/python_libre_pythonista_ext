from __future__ import annotations
from typing import Any, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT


_KEY = "libre_pythonista_lib.init.init_sheet.InitSheet"


# Composite Command
class CmdInitSheets(CmdBase, List[Type[CmdDocT]], LogMixin, CmdDocT):
    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        list.__init__(self)
        LogMixin.__init__(self)
        self.executed_commands: List[CmdDocT] = []
        self._doc = doc
        self.append(CmdSheetsModified)
        self.append(CmdSheetActivation)

    def execute(self) -> None:
        """
        Executes a series of commands as part of a composite command.
        This method retrieves the current document's global state and checks a specific key in the memory cache.
        If the key's value is "1", the method sets the success flag to True and returns immediately.
        Otherwise, it iterates over the commands, executing each one and collecting successful commands.
        If any command fails, it logs the failure, undoes all previously executed commands, and sets the success flag to False.
        If all commands succeed, it sets the success flag to True and updates the memory cache key to "1".
        In case of an unexpected exception, it logs the exception, undoes all executed commands, and sets the success flag to False.

        Returns:
            None: This method does not return anything.
        """

        doc_globals = DocGlobals.get_current()
        key_val = doc_globals.mem_cache[_KEY]
        if key_val == "1":
            self.success = True
            return
        try:
            for cmd in self:
                inst = cmd(self._doc)
                self._execute_cmd(inst)
                if inst.success:  # Only add if command was successful
                    self.executed_commands.append(inst)
                else:
                    self.log.debug("A command failed. Undoing previously executed commands.")
                    self.undo()  # Undo all successfully executed commands.
                    self.success = False  # Composite command failed.
                    return
            self.success = True  # Composite command succeeded.
            doc_globals.mem_cache[_KEY] = "1"
        except Exception as e:
            self.log.exception("An unexpected error occurred: %s", e)
            self.undo()
            self.success = False

        if self.success:
            self.log.debug("Successfully executed command.")

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

        for cmd in reversed(self.executed_commands):
            cmd.undo()
        self.executed_commands = []  # Clear executed commands
        self.success = False  # Reset success flag.
        doc_globals = DocGlobals.get_current()
        doc_globals.mem_cache[_KEY] = "0"
