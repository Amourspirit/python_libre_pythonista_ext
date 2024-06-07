# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import uno
import unohelper

# os.environ["OOODEV_SKIP_AUTOLOAD"] = "1"

from com.sun.star.task import XJob

if TYPE_CHECKING:
    # just for design time
    from libre_pythonista.oxt_logger import OxtLogger

# endregion imports

# region Constants

implementation_name = "com.github.amourspirit.extensions.librepythonista.LibrePythonistaLoadedJob"
implementation_services = ("com.sun.star.task.Job",)

# endregion Constants


# region XJob
class LibrePythonistaLoadedJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._logger = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        print("LibrePythonistaLoadedJob execute")
        self._logger.debug("LibrePythonistaLoadedJob execute")
        try:
            # loader = Lo.load_office()
            self._logger.debug(f"Args Length: {len(args)}")
            arg1 = args[0]

            for struct in arg1.Value:
                self._logger.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._logger.debug("Document Found")
            # assert loader is not None
            # self._logger.debug("Loader has Loaded")
            # inst = Lo.current_lo
            # assert inst is not None
            # self._logger.debug("Lo Instance has Loaded")
            # sc = Lo.XSCRIPTCONTEXT
            # assert sc is not None
            # self._logger.debug("Script Context has Loaded")
            # doc = sc.getDocument()
            # assert doc is not None
            # self._logger.debug("Document has Loaded")
            if self.document is None:
                self._logger.debug("LibrePythonistaLoadedJob - Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
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
        return OxtLogger(log_name="LibrePythonistaLoadedJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
# python loader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()

# add the FormatFactory class to the implementation container,
# which the loader uses to register/instantiate the component.
g_ImplementationHelper.addImplementation(LibrePythonistaLoadedJob, implementation_name, implementation_services)

# endregion Implementation
