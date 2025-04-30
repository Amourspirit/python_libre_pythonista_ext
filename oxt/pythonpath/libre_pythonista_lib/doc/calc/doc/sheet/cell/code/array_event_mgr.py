from __future__ import annotations
from typing import Any, cast, List, TYPE_CHECKING
import threading

from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_array_cells import QryArrayCells
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_update_array_formula import (
        CmdUpdateArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import PYC_RULE_MATCH_DONE
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.doc.qry_array_cells import QryArrayCells
    from libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_update_array_formula import CmdUpdateArrayFormula
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.const.event_const import PYC_RULE_MATCH_DONE

    QryHandlerT = Any
    CmdHandlerT = Any

_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.array_event_mgr.CellEventMgr"


class ArrayEventMgr(LogMixin):
    def __new__(cls, doc: CalcDoc) -> ArrayEventMgr:
        gbl_cache = DocGlobals.get_current(doc.runtime_uid)
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self, doc: CalcDoc) -> None:
        """
        Constructor

        Args:
            src_mgr (PySourceManager): The source manager to manage events for.
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self._doc = doc
        self._se = SharedEvent(self._doc)
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._is_init_calculate = False
        self._init_events()
        self._se.subscribe_event(PYC_RULE_MATCH_DONE, self._fn_on_pyc_rule_matched)
        self.log.debug("Init done for doc: %s", doc.runtime_uid)
        self._is_init = True

    def _qry_init_calculate(self) -> bool:
        qry = QryInitCalculate(uid=self._doc.runtime_uid)
        return self._qry_handler.handle(qry)

    def _init_events(self) -> None:
        self._fn_on_pyc_rule_matched = self._on_pyc_rule_matched

    # region PYC Events
    def _on_pyc_rule_matched(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        # this event is raised in PY.C when a rule is matched.
        # So, basically every call to PY.C will raise this event.
        try:
            self.log.debug("_on_pyc_rule_matched() Entering.")
            if not self._is_init_calculate:
                self._is_init_calculate = self._qry_init_calculate()
                if not self._is_init_calculate:
                    self.log.debug("_on_pyc_rule_matched()Document init CalculateAll not yet called. returning.")
                    return
            dd = cast(DotDict, event.event_data)
            if self.log.is_debug:
                self.log.debug("Is First Cell: %s", dd.is_first_cell)
                self.log.debug("Is Last Cell: %s", dd.is_last_cell)

            if dd.is_last_cell:
                # it is imperative that the update be called in a new thread.
                # If not called in a new thread then chances are LibreOffice will totally crash.
                # Most likely the crash is because a re-calculation of the sheet is taking place,
                # and the update that can change the sheet cell formulas is being called at the same time.
                # By calling in a thread the crash is avoided and the sheet is updated without any issues.
                t = threading.Thread(
                    target=update_array_cells,
                    args=(self._doc, self._qry_handler, self._cmd_handler, self.log),
                    daemon=True,
                )
                t.start()

        except Exception:
            self.log.exception("_on_pyc_rule_matched()")
            raise

        self.log.debug("_on_pyc_rule_matched() Done")

    # endregion PYC Events


def update_array_cells(doc: CalcDoc, qry_handler: QryHandlerT, cmd_handler: CmdHandlerT, log: OxtLogger) -> None:
    def qry_array_cells() -> List[CalcCell]:
        qry = QryArrayCells(doc=doc)
        result = qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        log.error("Failed to get array cells: %s", result.error)
        return []

    try:
        for calc_cell in qry_array_cells():
            cmd = CmdUpdateArrayFormula(cell=calc_cell)
            cmd_handler.handle(cmd)
            if not cmd.success:
                raise Exception("Failed to execute command for cell %s.", calc_cell.cell_obj)
    except Exception as e:
        log.exception("Error updating array cells: %s.", e)
