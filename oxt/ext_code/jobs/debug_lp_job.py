# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import contextlib
import os

import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        result = RequirementsCheck().run_imports_ready()
        if not result:
            return False
        try:
            __import__("debugpy")
        except (ModuleNotFoundError, ImportError):
            return False
    return True


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.basic_config import BasicConfig
    import debugpy  # type: ignore

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:

    def override(func):
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        import debugpy

        try:
            from ___lo_pip___.basic_config import BasicConfig
        except (ModuleNotFoundError, ImportError):
            _CONDITIONS_MET = False
# endregion imports


# region XJob
class DebugLpJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.DebugLpJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:
        # This job may be executed more then once.
        # When a spreadsheet is put into print preview this is fired.
        # When the print preview is closed this is fired again.
        # print("ViewJob execute")
        self._log.debug("DebugLpJob execute")
        if not _CONDITIONS_MET:
            return
        try:
            if os.getenv("ENABLE_LIBREPYTHONISTA_DEBUG"):
                basic_config = BasicConfig()
                # Start the debug server on port 5678
                debugpy.listen(("localhost", basic_config.lp_debug_port))
                self._log.debug(
                    "Waiting for debugger attach on port %i ...",
                    basic_config.lp_debug_port,
                )

                # Pause execution until debugger is attached
                debugpy.wait_for_client()
                os.environ.pop("ENABLE_LIBREPYTHONISTA_DEBUG")
                os.environ["LIBREPYTHONISTA_DEBUG_ATTACHED"] = "1"
                self._log.debug("Debugger attached.")
            else:
                self._log.debug("Debugging is disabled")
            # loader = Lo.load_office()
            self._log.debug(f"Args Length: {len(Arguments)}")

        except Exception:
            self._log.exception("Error getting current document")
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="DebugLpJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*DebugLpJob.get_imple())

# endregion Implementation