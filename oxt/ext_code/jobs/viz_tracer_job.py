# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import contextlib
import os


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
    from ...___lo_pip___.basic_config import BasicConfig
    from ...___lo_pip___.debug.viz_tracer_mgr import VizTracerMgr

else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        try:
            from ___lo_pip___.basic_config import BasicConfig
            from ___lo_pip___.debug.viz_tracer_mgr import VizTracerMgr
        except (ModuleNotFoundError, ImportError):
            _CONDITIONS_MET = False
# endregion imports


# region XJob
class VizTracerJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.VizTracerJob"
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
            if os.getenv("ENABLE_LIBREOFFICE_TRACER"):
                tracer_mgr = VizTracerMgr()

                self._log.debug("Starting VizTracerMgr")
                tracer_mgr.start()
                # debugpy.trace_this_thread(True)
                os.environ.pop("ENABLE_LIBREOFFICE_TRACER")
                os.environ["LIBREOFFICE_TRACER_STARTED"] = "1"
                self._log.debug("VizTracerMgr started.")
            else:
                self._log.debug("VizTracerMgr is disabled")

        except Exception:
            self._log.exception("Error starting VizTracerMgr")
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="VizTracerJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}  # noqa: N816
g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*VizTracerJob.get_imple())

# endregion Implementation
