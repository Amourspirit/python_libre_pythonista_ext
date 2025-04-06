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
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
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
        from libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
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
        # This job may be executed more then once or not at all.
        # When a spreadsheet is put into print preview this is fired.
        # When the print preview is closed this is fired again.
        # print("ViewJob execute")
        # Load Finished Job is not fired by LibreOffice when a new document is created.
        # It is fired when a document is loaded.
        self._log.debug("ViewJob execute")
        try:
            # loader = Lo.load_office()
            self._log.debug("Args Length: %i", len(Arguments))
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug("Struct: %s", struct.Name)
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")

            if self.document is None:
                self._log.debug("ViewJob - Document is None")
                return

            if _CONDITIONS_MET:
                self._lo_load(self.document)

            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document is a spreadsheet")
                return
                run_id = self.document.RuntimeUID
                key = f"LIBRE_PYTHONISTA_DOC_{run_id}"
                os.environ[key] = "1"
                self._log.debug("Added %s to environment variables", key)
                if _CONDITIONS_MET:
                    try:
                        self._log.debug("Conditions met. Continuing ...")
                        break_mgr.check_breakpoint("load_finished_job_init")
                        qry_handler = QryHandlerFactory.get_qry_handler()
                        cmd_handler = CmdHandlerFactory.get_cmd_handler()

                        doc = CalcDoc.get_doc_from_component(self.document)

                        qry_macro_mode = QryIsMacroEnabled(doc=doc)
                        macros_enabled = qry_handler.handle(qry_macro_mode)
                        if macros_enabled:
                            self._log.debug("Macros are enabled.")
                        else:
                            self._log.debug("Macros are not enabled. Exiting.")
                            return

                        qry = QryIsDocPythonista(doc=doc)
                        qry_result = qry_handler.handle(qry)
                        if Result.is_failure(qry_result):
                            self._log.error(
                                "Error checking if document is a LibrePythonista. Error: %s", qry_result.error
                            )
                            return
                        if not qry_result.data:
                            self._log.debug("Document is not a LibrePythonista. Returning.")
                            return

                        qry_calc_all = QryInitCalculate(uid=run_id)
                        if qry_handler.handle(qry_calc_all):
                            self._log.debug("Document has been calculated.")
                            return

                        self._log.debug("Document has not been calculated.")

                        cmd_calc_all = CmdCalculateAll(doc=doc)
                        cmd_handler.handle(cmd_calc_all)
                        if cmd_calc_all.success:
                            self._log.debug("Successfully calculated all formulas.")
                            cmd_init_calc = CmdInitCalculate(uid=run_id)
                            cmd_handler.handle(cmd_init_calc)
                            if cmd_init_calc.success:
                                self._log.debug("Successfully executed command.")
                            else:
                                self._log.error("Error executing command.")
                        else:
                            self._log.error("Error calculating all formulas.")
                        return

                    except Exception:
                        self._log.error("Error setting components on view.", exc_info=True)

                    # no longer needs to listen for the DocGlobals.get_current event.
                    self._events.remove(GET_CURRENT_EVENT, self._fn_on_get_current)
                else:
                    self._log.debug("Conditions not met to register dispatch manager")
            else:
                self._log.debug("Document is not a spreadsheet")

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
