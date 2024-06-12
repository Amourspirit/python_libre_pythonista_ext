# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import contextlib
import os
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
    from ooodev.loader import Lo
    from .pythonpath.libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
    from .pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr  # type: ignore
    from .pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from .pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
        CodeSheetActivationListener,
    )
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
        from libre_pythonista_lib.cell.cell_mgr import CellMgr  # type: ignore
        from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
        from libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
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
                self._logger.debug("Document recalculated")
                if _CONDITIONS_MET:
                    try:
                        self._logger.debug("Registering dispatch manager")
                        from ooodev.calc import CalcDoc

                        # Lo.load_office() only loads office if it is not already loaded
                        # It is needed here or the dispatch manager will not receive the correct document
                        # when multiple documents are open.
                        _ = Lo.load_office()
                        doc = CalcDoc.get_doc_from_component(self.document)

                        for sheet in doc.sheets:
                            unique_id = sheet.unique_id
                            if not CodeSheetModifyListener.has_listener(unique_id):
                                listener = CodeSheetModifyListener(unique_id)  # singleton
                                sheet.component.addModifyListener(listener)

                        view = doc.get_view()
                        view.component.addActivationEventListener(CodeSheetActivationListener())

                        self._logger.debug(f"Pre Dispatch manager loaded, UID: {doc.runtime_uid}")
                        dispatch_mgr.register_interceptor(doc)
                        cm = CellMgr(doc)
                        cm.reset_py_inst()
                        cm.add_all_listeners()

                        self.document.calculateAll()
                    except Exception:
                        self._logger.error("Error setting components on view.", exc_info=True)
                else:
                    self._logger.debug("Conditions not met to register dispatch manager")
                self._logger.debug("Dispatch manager registered")
            else:
                self._logger.debug("Document is not a spreadsheet")

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger

        return OxtLogger(log_name="LibrePythonistaViewJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(LibrePythonistaViewJob, implementation_name, implementation_services)

# endregion Implementation
