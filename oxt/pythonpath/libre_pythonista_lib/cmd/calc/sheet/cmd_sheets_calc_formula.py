from __future__ import annotations
from typing import Any, cast, List, TYPE_CHECKING
import time

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    CmdSheetCacheT = Any


class CmdSheetsCalcFormula(LogMixin, CmdT):
    """Add OnCalculate event to all sheets"""

    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._success_cmds: List[CmdSheetCacheT] = []

    def execute(self) -> None:
        self._success = False
        self._success_cmds.clear()
        try:
            handler = CmdHandler()
            for sheet in self._doc.sheets:
                cmd = CmdSheetCalcFormula(sheet)
                handler.handle(cmd)
                self._success = cmd.success
                if self._success:
                    self._success_cmds.append(cmd)
                else:
                    self.log.error("Error setting sheet calculate event for sheet %s", sheet.name)
                    break

            if not self._success:
                self._undo()

        except Exception:
            self.log.exception("Error setting sheet calculate event")
            self._undo()
            return
        self.log.debug("Successfully executed command")

    def _undo(self) -> None:
        try:
            for cmd in self._success_cmds:
                cmd.undo()
            self.log.debug("Successfully executed undo command")
        except Exception:
            self.log.exception("Error removing sheet calculate event")
        self._success_cmds.clear()

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        return CalcCmdKind.SIMPLE
