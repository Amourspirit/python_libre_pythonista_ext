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
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ooodev.utils.props import Props
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad

    break_mgr = BreakMgr()

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:

    def override(func):
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.utils.props import Props
        from ___lo_pip___.debug.break_mgr import BreakMgr
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad

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
                # self._log.debug(f"Added {key} to environment variables")
                if _CONDITIONS_MET:
                    try:
                        self._log.debug("Conditions met. Continuing ...")
                        break_mgr.check_breakpoint("view_job_init")
                        doc_args = self.document.getArgs()
                        args_dic = Props.props_to_dot_dict(doc_args)
                        if hasattr(args_dic, "MacroExecutionMode"):
                            self._log.debug("MacroExecutionMode: %s", args_dic.MacroExecutionMode)
                            macros_enabled = args_dic.MacroExecutionMode == 4
                        else:
                            macros_enabled = False
                        self._log.debug("Macros Enabled: %s", macros_enabled)
                        if not macros_enabled:
                            self._log.debug("Macros are not enabled. Exiting.")
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
