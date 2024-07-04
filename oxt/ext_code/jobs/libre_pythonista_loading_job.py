# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import uno
import unohelper


from com.sun.star.task import XJob

if TYPE_CHECKING:
    # just for design time
    from ...___lo_pip___.oxt_logger import OxtLogger

# endregion imports


# region XJob
class LibrePythonistaLoadingJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.LibrePythonistaLoadingJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._logger = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
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
                self._logger.debug("Document Loading is a spreadsheet")
            else:
                self._logger.debug("Document Loading not a spreadsheet")

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger

        return OxtLogger(log_name="LibrePythonistaLoadingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*LibrePythonistaLoadingJob.get_imple())

# endregion Implementation
