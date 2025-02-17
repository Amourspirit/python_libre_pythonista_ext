from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING
import time


if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_script_url import QrySheetScriptUrl
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import (
        SHEET_HAS_CALCULATION_EVENT,
        SHEET_CALCULATION_EVENT,
    )
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import (
        QrySheetHasCalculationEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import (
        QrySheetCalculationEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache import QryHandlerSheetCache

else:
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_script_url import QrySheetScriptUrl
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from libre_pythonista_lib.const.cache_const import SHEET_HAS_CALCULATION_EVENT, SHEET_CALCULATION_EVENT
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import QrySheetCalculationEvent
    from libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache import QryHandlerSheetCache

# this class should be call in:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache

# Should be called with:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache


class CmdSheetCalcFormula(LogMixin, CmdSheetCacheT):
    """Add OnCalculate event to sheet"""

    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        self._success = False
        self._sheet = sheet
        self._has_calc_event = self._get_has_calculate_event()
        self._current_script = self._get_current_script()

    def _get_current_script(self) -> str | None:
        qry = QrySheetCalculationEvent(sheet=self._sheet)
        handler = QryHandlerSheetCache()
        return handler.handle(qry)

    def _get_has_calculate_event(self) -> bool:
        qry = QrySheetHasCalculationEvent(sheet=self._sheet)
        handler = QryHandlerSheetCache()
        result = handler.handle(qry)
        if result is None:
            return False
        return result

    def execute(self) -> None:
        self._success = False
        try:
            if self._has_calc_event:
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

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (SHEET_HAS_CALCULATION_EVENT, SHEET_CALCULATION_EVENT)
