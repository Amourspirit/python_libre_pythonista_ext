# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING, Tuple
import contextlib
import os
import sys

import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    result = False
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        result = RequirementsCheck().run_imports_ready("debugpy")
    return result


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.___lo_pip___.config import Config
    import debugpy  # type: ignore

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        import debugpy

        try:
            from ___lo_pip___.config import Config
        except (ModuleNotFoundError, ImportError):
            _CONDITIONS_MET = False
# endregion imports


# region XJob
class DebugLpJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.DebugLpJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # noqa: ANN401, N803
        # This job may be executed more then once.
        # When a spreadsheet is put into print preview this is fired.
        # When the print preview is closed this is fired again.
        # print("ViewJob execute")
        self._log.debug("DebugLpJob execute")
        if not _CONDITIONS_MET:
            return
        try:
            if os.getenv("ENABLE_LIBREPYTHONISTA_DEBUG"):
                if (
                    os.getenv("LIBREPYTHONISTA_DEBUG_ATTACHED") == "1"
                    or os.getenv("LIBREOFFICE_DEBUG_ATTACHED") == "1"
                ):
                    self._log.debug("Debugger already attached.")
                    return
                cfg = Config()
                # Start the debug server on port 5678
                if cfg.lp_debug_port > 0:
                    is_windows = sys.platform == "win32"
                    print(f"Waiting for debugger attach on port  {cfg.lp_debug_port}")
                    self._log.debug("Waiting for debugger attach on port %i ...", cfg.lp_debug_port)
                    if is_windows:
                        exe = sys.executable
                        try:
                            # see: https://github.com/microsoft/debugpy/issues/262
                            sys.executable = cfg.python_path
                            self._log.debug("Windows so temporary setting sys.executable to %s", sys.executable)
                            debugpy.listen(cfg.lp_debug_port)
                        finally:
                            sys.executable = exe
                    else:
                        debugpy.listen(cfg.lp_debug_port)

                else:
                    self._log.warning(
                        "Debug port not set. Must be set in tool.oxt.token.lp_debug_port of pyproject.toml file. Contact the developer."
                    )
                    return

                debugpy.wait_for_client()
                os.environ.pop("ENABLE_LIBREPYTHONISTA_DEBUG")
                os.environ["LIBREPYTHONISTA_DEBUG_ATTACHED"] = "1"
                # os.environ["LIBREOFFICE_DEBUG_ATTACHED"] = "1"
                self._log.debug("Debugger attached.")
            else:
                self._log.debug("Debugging is disabled")
            # loader = Lo.load_office()
            self._log.debug("Args Length: %i", len(Arguments))

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

g_TypeTable = {}  # noqa: N816
g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*DebugLpJob.get_imple())

# endregion Implementation
