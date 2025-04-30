from __future__ import annotations

from typing import TYPE_CHECKING

from ooodev.calc import CalcSheet
from ooodev.events.args.event_args import EventArgs


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_calculate_all import CmdCalculateAll
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_cache import CellCache
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import AFTER_CALCULATED_CELLS_MOVED
else:
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_calculate_all import CmdCalculateAll
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_cache import CellCache
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from libre_pythonista_lib.const.event_const import AFTER_CALCULATED_CELLS_MOVED


class ListenerAfterCalculateCellsMoved(LogMixin, TriggerStateMixin):
    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        TriggerStateMixin.__init__(self)
        self.log.debug("Init")
        self._sheet = sheet
        self._se = SharedEvent(sheet.calc_doc)
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._init_events()
        self.log.debug("Init done for sheet: %s", sheet.name)

    def _init_events(self) -> None:
        self._fn_on_cells_moved = self._on_cells_moved
        self._se.subscribe_event(AFTER_CALCULATED_CELLS_MOVED, self._fn_on_cells_moved)

    def _qry_py_src_mgr(self) -> PySourceManager:
        qry = QryPySrcMgr(doc=self._sheet.calc_doc)
        return self._qry_handler.handle(qry)

    def _on_cells_moved(self, src: object, event: EventArgs) -> None:
        try:
            self.log.debug("_on_cells_moved() Entering.")
            if not self.is_trigger():
                self.log.debug("modified() Trigger events is False. Returning.")
                return
            py_src_mgr = self._qry_py_src_mgr()
            py_src_mgr.clear_instance_cache()
            py_src_mgr = None

            cell_cache = CellCache(doc=self._sheet.calc_doc)
            cell_cache.clear_instance_cache()
            cell_cache = None

            cmd = CmdCalculateAll(doc=self._sheet.calc_doc)
            self._cmd_handler.handle(cmd)
            if not cmd.success:
                self.log.error("Failed to execute command: CmdCalculateAll")

            self.log.debug("_on_cells_moved() Leaving.")
        except Exception as e:
            self.log.exception("Error executing query: %s", e)
