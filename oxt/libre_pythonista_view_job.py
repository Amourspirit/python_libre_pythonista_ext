# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import uno
import os
import unohelper


from com.sun.star.task import XJob

if TYPE_CHECKING:
    # just for design time
    from libre_pythonista.oxt_logger import OxtLogger

# endregion imports

# region Constants

implementation_name = "com.github.amourspirit.extensions.librepythonista.LibrePythonistaViewJob"
implementation_services = ("com.sun.star.task.Job",)

# endregion Constants


# region XJob
class LibrePythonistaViewJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._logger = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        print("LibrePythonistaViewJob execute")
        self._logger.debug("LibrePythonistaViewJob execute")
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
                self._logger.debug("LibrePythonistaViewJob - Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                key = f"LIBRE_PYTHONISTA_DOC_{self.document.RuntimeUID}"
                os.environ[key] = "1"
                self._logger.debug(f"Added {key} to environment variables")
                self.document.calculateAll()
                self._logger.debug("Document recalculated")
            else:
                self._logger.debug("Document is not a spreadsheet")

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from libre_pythonista.oxt_logger import OxtLogger
        return OxtLogger(log_name="LibrePythonistaViewJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(LibrePythonistaViewJob, implementation_name, implementation_services)

# endregion Implementation
