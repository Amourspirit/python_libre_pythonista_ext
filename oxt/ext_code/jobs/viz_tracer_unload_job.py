# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import contextlib
import os
from pathlib import Path

import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    result = False
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        result = RequirementsCheck().run_imports_ready("viztracer")

    return result


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.debug.viz_tracer_mgr import VizTracerMgr

else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        try:
            from ___lo_pip___.debug.viz_tracer_mgr import VizTracerMgr
        except (ModuleNotFoundError, ImportError):
            _CONDITIONS_MET = False
# endregion imports


# region XJob
class VizTracerUnloadJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.VizTracerUnloadJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> tuple:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()
        self._log.debug("init Done")

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # noqa: ANN401, N803
        self._log.debug("execute")
        if not _CONDITIONS_MET:
            return
        try:
            if os.getenv("LIBREOFFICE_TRACER_STARTED"):
                from ___lo_pip___.input_output import file_util

                tracer_mgr = VizTracerMgr()
                json_file = str(Path(file_util.get_user_profile_path(True), "viz_tracer.json"))

                self._log.debug("Stopping VizTracerMgr")

                tracer_mgr.stop(out_file=json_file)
                # debugpy.trace_this_thread(True)
                os.environ.pop("LIBREOFFICE_TRACER_STARTED")
                self._log.debug("VizTracerMgr started.")
            else:
                self._log.debug("VizTracerMgr was not started")

        except Exception:
            self._log.exception("Error unloading VizTracerMgr")
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="VizTracerUnloadJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}  # noqa: N816
g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*VizTracerUnloadJob.get_imple())

# endregion Implementation
