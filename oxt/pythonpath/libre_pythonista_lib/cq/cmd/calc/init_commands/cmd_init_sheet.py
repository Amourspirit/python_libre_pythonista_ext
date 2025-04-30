from __future__ import annotations
from typing import Any, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_ensure_forms import CmdSheetEnsureForms
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_event_mgr import QrySheetEventMgr
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_ensure_forms import CmdSheetEnsureForms
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_event_mgr import QrySheetEventMgr

    CalcSheet = Any

_KEY = "libre_pythonista_lib.init.init_sheet.InitSheet"


class CmdInitSheet(CmdBase, List[Type[CmdSheetT]], LogMixin, CmdSheetT):
    def __init__(self, sheet: CalcSheet) -> None:
        CmdBase.__init__(self)
        list.__init__(self)
        LogMixin.__init__(self)
        self._success_cmds: List[CmdSheetT] = []
        self._sheet = sheet
        self._cache = get_sheet_cache(self._sheet)
        self.append(CmdSheetCalcFormula)
        self.append(CmdSheetEnsureForms)
        self.log.debug("init done for sheet %s", sheet.name)

    def _init_queries(self) -> None:
        """
        Initializes the queries for the document.
        """
        # SheetEventMgr for new sheets are init via sheet.listen.code_sheet_activation_listener.CodeSheetActivationListener
        qry_sheet_event_mgr = QrySheetEventMgr(sheet=self._sheet)
        self._execute_qry(qry_sheet_event_mgr)
        self.log.debug("Init QrySheetEventMgr done.")

    @override
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

        key_val = self._cache[_KEY]
        if key_val == "1":
            self.success = True
            return
        try:
            for cmd in self:
                inst = cmd(self._sheet)
                self._execute_cmd(inst)
                if inst.success:  # Only add if command was successful
                    self._success_cmds.append(inst)
                else:
                    self.log.debug("A command failed. Undoing previously executed commands.")
                    self._undo()  # Undo all successfully executed commands.
                    self.success = False  # Batch command failed.
                    return
            self._init_queries()
            self.success = True  # Batch command succeeded.
            self._cache[_KEY] = "1"
        except Exception as e:
            self.log.exception("An unexpected error occurred: %s", e)
            self.undo()
            self.success = False

        if self.success:
            self.log.debug("Successfully executed command.")

    def _undo(self) -> None:
        for cmd in reversed(self._success_cmds):
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()  # Clear executed commands
        self.success = False  # Reset success flag.

        self._cache[_KEY] = "0"

    @override
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
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
