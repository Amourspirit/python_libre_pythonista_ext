# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import os
import contextlib
import uno
import unohelper


from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    # just for design time
    _CONDITIONS_MET = True
    from .___lo_pip___.oxt_logger import OxtLogger
else:
    _CONDITIONS_MET = _conditions_met()
# endregion imports

# region Constants

implementation_name = "com.github.amourspirit.extensions.librepythonista.LibrePythonistaUnLoadingJob"
implementation_services = ("com.sun.star.task.Job",)

# endregion Constants


# region XJob
class LibrePythonistaUnLoadingJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._logger = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        print("LibrePythonistaUnLoadingJob execute")
        self._logger.debug("execute")
        try:
            # loader = Lo.load_office()
            self._logger.debug(f"Args Length: {len(args)}")
            arg1 = args[0]

            for struct in arg1.Value:
                self._logger.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._logger.debug("Document Found")
            if self.document is None:
                self._logger.debug("Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._logger.debug("Document UnLoading is a spreadsheet")
                key = f"LIBRE_PYTHONISTA_DOC_{self.document.RuntimeUID}"
                if key in os.environ:
                    self._logger.debug(f"Removing {key} from os.environ")
                    del os.environ[key]
                else:
                    self._logger.debug(f"{key} not found in os.environ")
                if _CONDITIONS_MET:
                    try:
                        from ooodev.calc import CalcDoc

                        doc = CalcDoc.from_current_doc()
                        from libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore

                        dispatch_mgr.unregister_interceptor(doc)
                    except Exception as e:
                        self._logger.error("Error unregistering dispatch manager", exc_info=True)
            else:
                self._logger.debug("Document UnLoading not a spreadsheet")

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from libre_pythonista.oxt_logger import OxtLogger

        return OxtLogger(log_name="LibrePythonistaUnLoadingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(LibrePythonistaUnLoadingJob, implementation_name, implementation_services)

# endregion Implementation
