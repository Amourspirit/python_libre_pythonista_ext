# region imports
from __future__ import unicode_literals, annotations
from typing import Any, Tuple, TYPE_CHECKING
import contextlib

import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ooodev.calc import CalcDoc
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_is_calc_view import QryIsCalcView
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_register_dispatch_interceptor import (
        CmdRegisterDispatchInterceptor,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_unregister_dispatch_interceptor import (
        CmdUnRegisterDispatchInterceptor,
    )

    break_mgr = BreakMgr()

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc  # noqa: F401
        from ___lo_pip___.debug.break_mgr import BreakMgr
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
        from libre_pythonista_lib.cq.qry.calc.doc.qry_is_calc_view import QryIsCalcView
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_register_dispatch_interceptor import (
            CmdRegisterDispatchInterceptor,
        )
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_unregister_dispatch_interceptor import (
            CmdUnRegisterDispatchInterceptor,
        )

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        # break_mgr.add_breakpoint("view_job_init")
        # break_mgr.add_breakpoint("view_job_init_state")
# endregion imports


# region XJob
class ViewJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.ViewJob"
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
        self._log.debug("init Done")

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
        # This job may be executed more then once.
        # When a spreadsheet is put into print preview this is fired.
        # When the print preview is closed this is fired again.
        # print("ViewJob execute")
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
                # run_id = self.document.RuntimeUID
                # key = f"LIBRE_PYTHONISTA_DOC_{run_id}"
                # os.environ[key] = "1"
                # self._log.debug(f"Added {key} to environment variables"
                self._log.debug("Document is a spreadsheet")

                if _CONDITIONS_MET:
                    qry_handler = QryHandlerFactory.get_qry_handler()
                    cmd_handler = CmdHandlerFactory.get_cmd_handler()

                    try:
                        self._log.debug("Conditions met. Continuing ...")
                        break_mgr.check_breakpoint("view_job_init")
                        doc = CalcDoc.get_doc_from_component(self.document)

                        qry_macro_mode = QryIsMacroEnabled(doc=doc)
                        macros_enabled = qry_handler.handle(qry_macro_mode)
                        if macros_enabled:
                            self._log.debug("Macros are enabled.")
                        else:
                            self._log.debug("Macros are not enabled. Exiting.")
                            return

                        qry = QryIsCalcView(doc=doc)
                        if qry_handler.handle(qry):
                            self._log.debug("Document is a Calc view.")
                            cmd = CmdRegisterDispatchInterceptor(doc=doc)
                            cmd_handler.handle(cmd)
                            if cmd.success:
                                self._log.debug("Successfully registered dispatch interceptor.")
                            else:
                                self._log.warning("Failed to register dispatch interceptor.")
                        else:
                            self._log.debug("Document is not a Calc view. Returning.")
                            cmd = CmdUnRegisterDispatchInterceptor(doc=doc)
                            cmd_handler.handle(cmd)
                            if cmd.success:
                                self._log.debug("Successfully unregistered dispatch interceptor.")
                            else:
                                self._log.warning("Failed to unregister dispatch interceptor.")
                            return

                    except Exception:
                        self._log.error("Error setting components on view.", exc_info=True)
                else:
                    self._log.debug("Conditions not met to register dispatch manager")
            else:
                self._log.debug("Document is not a spreadsheet")

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="ViewJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*ViewJob.get_imple())

# endregion Implementation
