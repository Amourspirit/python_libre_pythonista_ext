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
    from ..___lo_pip___.oxt_logger import OxtLogger
    from ..___lo_pip___.config import Config
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ___lo_pip___.config import Config
# endregion imports

# region Constants

implementation_name = "com.github.amourspirit.extensions.librepythonista.LibrePythonistaSavingJob"
implementation_services = ("com.sun.star.task.Job",)

# endregion Constants


# region XJob
class LibrePythonistaSavingJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._logger = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        print("LibrePythonistaSavingJob execute")
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
                self._logger.debug("Document Saving is a spreadsheet")
                if _CONDITIONS_MET:
                    try:
                        from ooodev.calc import CalcDoc

                        doc = CalcDoc.get_doc_from_component(self.document)
                        cfg = Config()
                        ver = doc.get_custom_property("LIBRE_PYTHONISTA_VERSION", "")
                        if ver != cfg.extension_version:
                            doc.set_custom_property("LIBRE_PYTHONISTA_VERSION", cfg.extension_version)

                    except Exception as e:
                        self._logger.error("Error Setting Custom Properties", exc_info=True)
            else:
                self._logger.debug("Document UnLoading not a spreadsheet")

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from libre_pythonista.oxt_logger import OxtLogger

        return OxtLogger(log_name="LibrePythonistaSavingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(LibrePythonistaSavingJob, implementation_name, implementation_services)

# endregion Implementation
