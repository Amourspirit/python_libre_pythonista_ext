from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING
import time


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
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
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.menus.cell_reg_interceptor import (
        register_interceptor,
        unregister_interceptor,
    )
    from oxt.pythonpath.libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import (
        CalcSheetCellDispatchProvider,
    )

else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.const.cache_const import SHEET_HAS_CALCULATION_EVENT, SHEET_CALCULATION_EVENT
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import QrySheetCalculationEvent
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.menus.cell_reg_interceptor import register_interceptor, unregister_interceptor
    from libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import CalcSheetCellDispatchProvider

# Should be called with:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache


class CmdRegisterDispatchInterceptor(LogMixin, CmdT):
    """Add OnCalculate event to sheet"""

    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        self._success = False
        self._doc = doc
        self._kind = CalcCmdKind.SIMPLE
        self._has_instance = CalcSheetCellDispatchProvider.has_instance(doc)

    def execute(self) -> None:
        self._success = False
        try:
            if self._has_instance:
                self.log.debug("Dispatch Provider Interceptor already registered.")
                self._success = True
                return
            register_interceptor(self._doc)
            self._has_instance = CalcSheetCellDispatchProvider.has_instance(self._doc)
        except Exception as e:
            self.log.exception("Error registering Dispatch Provider Interceptor. Error: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            if CalcSheetCellDispatchProvider.has_instance(self._doc):
                unregister_interceptor(self._doc)
                self._has_instance = CalcSheetCellDispatchProvider.has_instance(self._doc)
            else:
                self.log.debug("Dispatch Provider Interceptor not registered.")
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error unregistering Dispatch Provider Interceptor")

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
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
