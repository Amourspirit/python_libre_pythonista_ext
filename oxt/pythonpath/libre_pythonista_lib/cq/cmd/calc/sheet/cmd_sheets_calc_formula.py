from __future__ import annotations
from typing import Any, cast, List, TYPE_CHECKING

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula


class CmdSheetsCalcFormula(CmdBase, LogMixin, CmdT):
    """Add OnCalculate event to all sheets"""

    def __init__(self) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success_cmds: List[CmdSheetCacheT] = []
        self.log.debug("init done")

    @override
    def execute(self) -> None:
        self.success = False
        self._success_cmds.clear()
        try:
            for sheet in self._doc.sheets:
                cmd = CmdSheetCalcFormula(sheet)
                self._execute_cmd(cmd)
                self.success = cmd.success
                if self.success:
                    self._success_cmds.append(cmd)
                else:
                    self.log.error("Error setting sheet calculate event for sheet %s", sheet.name)
                    break

            if not self.success:
                self._undo()

        except Exception:
            self.log.exception("Error setting sheet calculate event")
            self._undo()
            return
        self.log.debug("Successfully executed command")

    def _undo(self) -> None:
        try:
            for cmd in self._success_cmds:
                self._execute_cmd_undo(cmd)
            self.log.debug("Successfully executed undo command")
        except Exception:
            self.log.exception("Error removing sheet calculate event")
        self._success_cmds.clear()

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
