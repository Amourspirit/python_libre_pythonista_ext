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
    from ooodev.calc import CalcDoc
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.config import Config
    from ...pythonpath.libre_pythonista_lib.code.py_source_mgr import PyInstance
    from ...pythonpath.libre_pythonista_lib.sheet.calculate import remove_doc_sheets_calculate_event
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ___lo_pip___.config import Config
        from libre_pythonista_lib.code.py_source_mgr import PyInstance
        from libre_pythonista_lib.sheet.calculate import remove_doc_sheets_calculate_event
# endregion imports


# region XJob
class SavingJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.SavingJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx):
        XJob.__init__(self)
        unohelper.Base.__init__(self)
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
                self._logger.debug("Document Saving is a spreadsheet")
                if _CONDITIONS_MET:
                    doc = CalcDoc.get_doc_from_component(self.document)
                    try:
                        cfg = Config()
                        ver = doc.get_custom_property("LIBRE_PYTHONISTA_VERSION", "")
                        if ver != cfg.extension_version:
                            doc.set_custom_property("LIBRE_PYTHONISTA_VERSION", cfg.extension_version)

                    except Exception as e:
                        self._logger.error("Error Setting Custom Properties", exc_info=True)

                    try:
                        py_src = PyInstance(doc)  # singleton
                        if not py_src.has_code():
                            self._logger.debug("No Code Found for document")
                            remove_doc_sheets_calculate_event(doc)
                        else:
                            self._logger.debug("Code Found for document")
                    except Exception as e:
                        self._logger.error("Error removing unused Sheet Events", exc_info=True)
            else:
                self._logger.debug("Document UnLoading not a spreadsheet")

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="SavingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*SavingJob.get_imple())

# endregion Implementation