from __future__ import annotations
from typing import List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_doc_event import CmdDocEvent
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_code_sheet_activation_listener import (
        CmdCodeSheetActivation,
    )
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_form_design_mode_off import CmdFormDesignModeOff
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.cmd_register_dispatch_interceptor import (
        CmdRegisterDispatchInterceptor,
    )
else:
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cmd.calc.doc.listener.cmd_doc_event import CmdDocEvent
    from libre_pythonista_lib.cmd.calc.doc.listener.cmd_code_sheet_activation_listener import CmdCodeSheetActivation
    from libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    from libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cmd.calc.doc.listener.cmd_form_design_mode_off import CmdFormDesignModeOff
    from libre_pythonista_lib.cmd.calc.doc.cmd_register_dispatch_interceptor import CmdRegisterDispatchInterceptor


_KEY = "libre_pythonista_lib.init.init_doc.InitDoc"


# Composite Command
class CmdInitDoc(List[Type[CmdDocT]], LogMixin, CmdDocT):
    """
    Composite command to initialize the document.
    """

    def __init__(self, doc: CalcDoc) -> None:
        list.__init__(self)
        LogMixin.__init__(self)
        self.append(CmdDocEvent)
        self.append(CmdCodeSheetActivation)
        self.append(CmdSheetsModified)
        self.append(CmdSheetActivation)
        self.append(CmdFormDesignModeOff)
        self.append(CmdRegisterDispatchInterceptor)
        self._success_cmds: List[CmdDocT] = []
        self._success = False
        self._doc = doc
        self._handler = CmdHandler()
        self._kind = CalcCmdKind.SIMPLE

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
            self._success = True
            return
        self._success = False
        try:
            for cmd in self:
                inst = cmd(self._doc)
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
            doc_globals.mem_cache[_KEY] = "1"
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
        doc_globals = DocGlobals.get_current()
        doc_globals.mem_cache[_KEY] = "0"

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
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        """Gets if the command was successful."""
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
