# region imports
from __future__ import unicode_literals, annotations
from typing import Any, Tuple, TYPE_CHECKING
import contextlib
import os

import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ooodev.calc import CalcDoc
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.___lo_pip___.events.args.event_args import EventArgs
    from oxt.___lo_pip___.events.lo_events import LoEvents
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_calculate_all import CmdCalculateAll
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_init_calculate import CmdInitCalculate
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import GET_CURRENT_EVENT
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result

    break_mgr = BreakMgr()

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ___lo_pip___.debug.break_mgr import BreakMgr
        from ___lo_pip___.events.args.event_args import EventArgs
        from ___lo_pip___.events.lo_events import LoEvents
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_calculate_all import CmdCalculateAll
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_init_calculate import CmdInitCalculate
        from libre_pythonista_lib.cq.qry.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
        from libre_pythonista_lib.doc.doc_globals import GET_CURRENT_EVENT
        from libre_pythonista_lib.utils.result import Result

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        break_mgr.add_breakpoint("load_finished_job_init")
        break_mgr.add_breakpoint("load_finished_job_init_state")
# endregion imports


# region XJob
class LoadFinishedJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.LoadFinishedJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: object) -> None:
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()
        self._log.debug("init")
        if _CONDITIONS_MET:
            # subscribe to the DocGlobals.get_current event and set the uid for the current document.
            self._fn_on_get_current = self._on_get_current
            self._events = LoEvents()
            self._events.on(GET_CURRENT_EVENT, self._fn_on_get_current)

    # endregion Init

    def _lo_load(self, doc: Any) -> None:  # noqa: ANN401
        """Loads OooDev"""
        self._log.debug("_lo_load()_ Loading OooDev")
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        cmd = CmdCurrentCtxLoad(ctx=self.ctx, uid=doc.RuntimeUID)
        cmd_handler.handle(cmd)
        if not cmd.success:
            self._log.error("Error loading OooDev")
            return
        self._log.debug("OooDev Loaded")

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # noqa: ANN401, N803
        # Load Finished Job is not fired by LibreOffice when a new document is created.
        # It is fired when a document is loaded.
        self._log.debug("execute")
        try:
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug("Struct: %s", struct.Name)
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")

            if self.document is None:
                self._log.debug("Document is None")
                return

            if _CONDITIONS_MET:
                self._lo_load(self.document)

            run_id = self.document.RuntimeUID
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document %s is a spreadsheet", run_id)
            else:
                self._log.debug("Document %s is not a spreadsheet", run_id)

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Event Handlers

    def _on_get_current(self, source: Any, event: EventArgs) -> None:  # noqa: ANN401
        if self.document is not None:
            event.event_data["uid"] = self.document.RuntimeUID

    # endregion Event Handlers

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="LoadFinishedJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*LoadFinishedJob.get_imple())

# endregion Implementation
