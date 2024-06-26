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
    from ..pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from ..pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
        CodeSheetActivationListener,
    )
    from ..pythonpath.libre_pythonista_lib.code.mod_fn.lp_log import LpLog
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
        from libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
        from libre_pythonista_lib.code.mod_fn.lp_log import LpLog
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
                    run_time_id = self.document.RuntimeUID
                    try:
                        from ooodev.calc import CalcDoc

                        # doc = CalcDoc.from_current_doc()
                        doc = CalcDoc.get_doc_from_component(self.document)
                        from libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
                        from libre_pythonista_lib.cell.cell_mgr import CellMgr  # type: ignore

                        dispatch_mgr.unregister_interceptor(doc)
                        CellMgr.reset_instance(doc)
                        view = doc.get_view()
                        view.component.addActivationEventListener(CodeSheetActivationListener())
                        for sheet in doc.sheets:
                            unique_id = sheet.unique_id
                            if CodeSheetModifyListener.has_listener(unique_id):
                                listener = CodeSheetModifyListener(unique_id)  # singleton
                                sheet.component.removeModifyListener(listener)
                    except Exception as e:
                        self._logger.error("Error unregistering dispatch manager", exc_info=True)
                    try:
                        self._logger.debug("Cleaning up LpLog file")
                        lp_log = LpLog(run_time_id)
                        if lp_log.log_path.exists():
                            self._logger.debug(f"Removing LpLog file: {lp_log.log_path}")
                            lp_log.log_path.unlink()
                        LpLog.reset_instance(run_time_id)
                    except Exception as e:
                        self._logger.error("Error removing log file", exc_info=True)
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
