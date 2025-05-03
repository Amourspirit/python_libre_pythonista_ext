from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING, Union

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import (
        SHEET_HAS_CALCULATION_EVENT,
        SHEET_CALCULATION_EVENT,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_has_calculation_event import (
        QrySheetHasCalculationEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_calculation_event import (
        QrySheetCalculationEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from libre_pythonista_lib.const.cache_const import SHEET_HAS_CALCULATION_EVENT, SHEET_CALCULATION_EVENT
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_calculation_event import QrySheetCalculationEvent
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

# Should be called with:
# libre_pythonista_lib.cq.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache


class CmdSheetCalcFormula(CmdBase, LogMixin, CmdSheetCacheT):
    """Add OnCalculate event to sheet"""

    def __init__(self, sheet: CalcSheet) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SHEET_CACHE
        self._sheet = sheet
        self._has_calc_event = cast(bool, NULL_OBJ)
        self._current_script = cast(Union[str, None], NULL_OBJ)
        self.log.debug("init done for sheet %s", sheet.name)

    def _get_current_script(self) -> Union[str, None]:
        qry = QrySheetCalculationEvent(sheet=self._sheet)
        return self._execute_qry(qry)

    def _get_has_calculate_event(self) -> bool:
        qry = QrySheetHasCalculationEvent(sheet=self._sheet)
        result = self._execute_qry(qry)
        if result is None:
            return False
        return result

    @override
    def execute(self) -> None:
        if self._current_script is NULL_OBJ:
            self._current_script = self._get_current_script()

        if self._has_calc_event is NULL_OBJ:
            self._has_calc_event = self._get_has_calculate_event()

        self.success = False
        try:
            if self._has_calc_event:
                self.success = True
                return
            calculate.set_sheet_calculate_event(self._sheet)
        except Exception:
            self.log.exception("Error setting sheet calculate event")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if self._current_script:
                calculate.set_sheet_calculate_event(self._sheet, self._current_script)
            else:
                calculate.remove_doc_sheet_calculate_event(self._sheet)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error removing Document Event listener")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (SHEET_HAS_CALCULATION_EVENT, SHEET_CALCULATION_EVENT)
