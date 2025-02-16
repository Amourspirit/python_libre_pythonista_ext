from __future__ import annotations
from typing import cast, TYPE_CHECKING
import time

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.mixin.sheet_calculation_event_cache_key_mixin import (
        SheetCalculationEventCacheKeyMixin,
    )
else:
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cache.calc.sheet.mixin.sheet_calculation_event_cache_key_mixin import (
        SheetCalculationEventCacheKeyMixin,
    )

# this class should be call in:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache


class CmdSheetCalcFormula(LogMixin, SheetCalculationEventCacheKeyMixin, CmdT):
    """Add OnCalculate event to sheet"""

    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        SheetCalculationEventCacheKeyMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._sheet = sheet
        self._current_script = calculate.get_sheet_calculate_event(self._sheet)

    def execute(self) -> None:
        self._success = False
        try:
            if calculate.sheet_has_calculate_event(self._sheet):
                self._success = True
                return
            calculate.set_sheet_calculate_event(self._sheet)
        except Exception:
            self.log.exception("Error setting sheet calculate event")
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def undo(self) -> None:
        if self._success:
            try:
                if self._current_script:
                    calculate.set_sheet_calculate_event(self._sheet, self._current_script)
                else:
                    calculate.remove_doc_sheet_calculate_event(self._sheet)
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing Document Event listener")
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success
