from __future__ import annotations
from typing import cast, TYPE_CHECKING
import time

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdSheetsCalcFormula(LogMixin, CmdT):
    """Add OnCalculate event to all sheets"""

    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._current = []

    def _undo_current(self) -> None:
        for sheet, script in self._current:
            if script:
                calculate.set_sheet_calculate_event(sheet, script)
            else:
                calculate.remove_doc_sheet_calculate_event(sheet)

    def execute(self) -> None:
        self._success = False
        try:
            self._current.clear()
            for sheet in self._doc.sheets:
                if calculate.sheet_has_calculate_event(sheet):
                    self._success = True
                    continue
                current_script = calculate.get_sheet_calculate_event(sheet)
                self._success = calculate.set_sheet_calculate_event(sheet)
                if not self._success:
                    break
                self._current.append((sheet, current_script))
            if not self._success:
                self._undo_current()
                self._current.clear()

        except Exception:
            self.log.exception("Error setting sheet calculate event")
            return
        self.log.debug("Successfully executed command")
        self._success = True

    def undo(self) -> None:
        if self._success:
            try:
                self._undo_current()
                self._current.clear()
                self.log.debug("Successfully executed undo command")
            except Exception:
                self.log.exception("Error removing sheet calculate event")
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success
