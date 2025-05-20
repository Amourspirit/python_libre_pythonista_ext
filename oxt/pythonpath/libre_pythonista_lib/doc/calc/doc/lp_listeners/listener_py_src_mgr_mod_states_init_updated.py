from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcDoc
from ooodev.events.args.event_args import EventArgs


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_mode_states_init import CmdModeStatesInit
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_mode_states_init import QryModeStatesInit
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import PY_SRC_MGR_MOD_STATES_INIT_UPDATED
else:
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_mode_states_init import CmdModeStatesInit
    from libre_pythonista_lib.cq.qry.doc.qry_mode_states_init import QryModeStatesInit
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from libre_pythonista_lib.const.event_const import PY_SRC_MGR_MOD_STATES_INIT_UPDATED


class ListenerPySrcMgrModStatesInitUpdated(LogMixin, TriggerStateMixin):
    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        TriggerStateMixin.__init__(self)
        self.log.debug("Init")
        self._doc = doc
        self._se = SharedEvent(self._doc)
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._init_events()
        self.log.debug("Init done for doc: %s", doc.runtime_uid)

    def _qry_mode_states_init(self) -> bool:
        qry = QryModeStatesInit(uid=self._doc.runtime_uid)
        return self._qry_handler.handle(qry)

    def _init_events(self) -> None:
        self._fn_on_updated = self._on_updated
        self._se.subscribe_event(PY_SRC_MGR_MOD_STATES_INIT_UPDATED, self._fn_on_updated)

    def _on_updated(self, src: object, event: EventArgs) -> None:  # noqa: ANN401
        try:
            if self._qry_mode_states_init():
                return

            cmd = CmdModeStatesInit(doc=self._doc)
            self._cmd_handler.handle(cmd)
            if cmd.success:
                self.log.debug("Module States Init. DOC_MOD_STATES_INIT cache state set.")
            else:
                self.log.error("CmdModeStatesInit failed")
            self._doc.component.calculateAll()
        except Exception as e:
            self.log.exception("Error executing query: %s", e)
