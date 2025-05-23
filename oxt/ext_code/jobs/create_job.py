# region imports
from __future__ import unicode_literals, annotations
from typing import Any, Tuple, TYPE_CHECKING
import threading
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
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.utils.props import Props
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.debug.break_mgr import BreakMgr

    break_mgr = BreakMgr()

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ooodev.utils.props import Props
        from ___lo_pip___.debug.break_mgr import BreakMgr

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        # break_mgr.add_breakpoint("create_job_init")
        # break_mgr.add_breakpoint("create_job_init_state")
# endregion imports


# region XJob
class CreateJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.CreateJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx):
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()
        self._log.debug("init Done")

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:
        self._log.debug("CreateJob execute")
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
                self._log.debug("CreateJob - Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                run_id = self.document.RuntimeUID
                key = f"LIBRE_PYTHONISTA_DOC_{run_id}"
                os.environ[key] = "1"
                self._log.debug(f"Added {key} to environment variables")
                if _CONDITIONS_MET:
                    try:
                        self._log.debug("Conditions met. Continuing ...")
                        break_mgr.check_breakpoint("create_job_init")
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

                        _ = Lo.load_office()
                        doc = CalcDoc.get_doc_from_component(self.document)

                        t = threading.Thread(target=_init_with_state, args=(doc, self._log), daemon=True)
                        t.start()
                        # t.join() # DO NOT join. Can cause LibreOffice to hang.

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

        return OxtLogger(log_name="CreateJob")

    # endregion Logging


def _init_with_state(doc: CalcDoc, log: OxtLogger):
    # This method is run in a thread.
    # The reason for this on Ubuntu 20.04 is that the main thread crashes if there is a plot in the document python code.
    # This crash does not give any information in the logs.
    # After much testing and debugging I discovered that crash can be avoided if this code is run in a thread.
    # The crash did not happen Flatpak version, Snap Version, Windows version or Docker version. Only on Ubuntu 20.04 when apt installed so far.
    log.debug("_init_with_state()")
    if TYPE_CHECKING:
        from ...pythonpath.libre_pythonista_lib.doc.calc_doc_mgr import CalcDocMgr

    else:
        try:
            from libre_pythonista_lib.doc.calc_doc_mgr import CalcDocMgr

            log.debug("Imported CalcDocMgr")
        except ImportError:
            log.error("Error importing oxt_init and/or CalcStateMgr", exc_info=True)
            return

    try:
        log.debug("Creating an instance of CalcDocMgr")
        # if os.getenv("LIBREOFFICE_DEBUG_ATTACHED"):
        #     breakpoint()
        break_mgr.check_breakpoint("create_job_init_state")

        doc_mgr = CalcDocMgr()
        doc_mgr.calc_state_mgr.is_oxt_init = True
        # doc_mgr.ensure_events_for_new()
        doc_mgr.is_job_loading_finished = True

    except Exception:
        log.error("Error _init_with_state()", exc_info=True)


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*CreateJob.get_imple())

# endregion Implementation
