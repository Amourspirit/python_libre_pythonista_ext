from __future__ import annotations

from typing import TYPE_CHECKING

from ooodev.calc import CalcSheet
from ooodev.events.args.event_args import EventArgs


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_clear_cache import CmdClearCache
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_moved import QryLpCellsMoved
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELLS_MOVED
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import (
        CALC_FORMULAS_CALCULATED,
        AFTER_CALCULATED_CELLS_MOVED,
    )
else:
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_clear_cache import CmdClearCache
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_moved import QryLpCellsMoved
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from libre_pythonista_lib.const.cache_const import CELLS_MOVED
    from libre_pythonista_lib.const.event_const import CALC_FORMULAS_CALCULATED, AFTER_CALCULATED_CELLS_MOVED


class ListenerSheetCalculated(LogMixin, TriggerStateMixin):
    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        TriggerStateMixin.__init__(self)
        self.log.debug("Init")
        self._sheet = sheet
        self._se = SharedEvent(sheet.calc_doc)
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._init_events()
        self.log.debug("Init done for sheet: %s", sheet.name)

    def _init_events(self) -> None:
        self._fn_on_sheet_calculated = self._on_sheet_calculated
        self._se.subscribe_event(CALC_FORMULAS_CALCULATED, self._fn_on_sheet_calculated)

    def _qry_cells_moved(self) -> bool:
        """Queries if the cell has moved"""
        qry = QryLpCellsMoved(self._sheet)
        return self._qry_handler.handle(qry)

    def _on_sheet_calculated(self, src: object, event: EventArgs) -> None:  # noqa: ANN401
        try:
            cells_moved = self._qry_cells_moved()
            cmd = CmdClearCache(CELLS_MOVED, sheet=self._sheet)
            self._cmd_handler.handle(cmd)
            if cmd.success:
                self.log.debug("Sheet calculated. Cleared cache for CELLS_MOVED")
            else:
                self.log.error("Sheet calculated. Failed to clear cache for CELLS_MOVED")
            if cells_moved:
                self.log.debug("Sheet calculated. Cells moved.")
                self._se.trigger_event(AFTER_CALCULATED_CELLS_MOVED, event)
            else:
                self.log.debug("Sheet calculated. Cells not moved.")
        except Exception as e:
            self.log.exception("Error executing query: %s", e)
