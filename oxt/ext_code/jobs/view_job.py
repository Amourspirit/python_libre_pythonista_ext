# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
import threading
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
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ...___lo_pip___.oxt_logger import OxtLogger

    # from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
    #     SheetCalculationEventListener,
    # )
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
# endregion imports


# region XJob
class ViewJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.ViewJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        # This job may be executed more then once.
        # When a spreadsheet is put into print preview this is fired.
        # When the print preview is closed this is fired again.
        # print("ViewJob execute")
        self._log.debug("ViewJob execute")
        try:
            # loader = Lo.load_office()
            self._log.debug(f"Args Length: {len(args)}")
            arg1 = args[0]

            for struct in arg1.Value:
                self._log.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")

            if self.document is None:
                self._log.debug("ViewJob - Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                run_id = self.document.RuntimeUID
                key = f"LIBRE_PYTHONISTA_DOC_{run_id}"
                os.environ[key] = "1"
                self._log.debug(f"Added {key} to environment variables")
                if _CONDITIONS_MET:
                    try:
                        self._log.debug("Conditions met. Continuing ...")
                        _ = Lo.load_office()
                        doc = CalcDoc.get_doc_from_component(self.document)
                        t = threading.Thread(target=_init_with_state, args=(doc, self._log), daemon=True)
                        t.start()
                        # t.join() # DO NOT join. Can cause LibreOffice to hang.

                    except Exception:
                        self._log.error("Error setting components on view.", exc_info=True)
                else:
                    self._log.debug("Conditions not met to register dispatch manager")
            else:
                self._log.debug("Document is not a spreadsheet")

        except Exception as e:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="ViewJob")

    # endregion Logging


def _init_with_state(doc: CalcDoc, log: OxtLogger):
    # This method is run in a thread.
    # The reason for this on Ubuntu 20.04 is that the main thread crashes if there is a plot in the document python code.
    # This crash does not give any information in the logs.
    # After much testing and debugging I discovered that crash can be avoided if this code is run in a thread.
    # The crash did not happen Flatpak version, Snap Version, Windows version or Docker version. Only on Ubuntu 20.04 when apt installed so far.
    log.debug("_init_with_state()")
    if TYPE_CHECKING:
        from ...pythonpath.libre_pythonista_lib.oxt_init import oxt_init
        from ...pythonpath.libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
    else:
        try:
            from libre_pythonista_lib.oxt_init import oxt_init
            from libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr

            log.debug("Imported oxt_init and CalcStateMgr")
        except ImportError:
            log.error("Error importing oxt_init and/or CalcStateMgr", exc_info=True)
            return

    try:
        log.debug("Creating an instance of CalcStateMgr")
        state_mgr = CalcStateMgr(doc)
        log.debug("Document Loaded State Manager")
        if state_mgr.is_oxt_init:
            log.debug("oxt_init() state_mgr reports already init")
        else:
            log.debug("Running oxt_init()")
            oxt_init(doc.component, log, state_mgr)
            state_mgr.is_oxt_init = True
            log.debug("oxt_init() done.")
    except Exception:
        log.error("Error _init_with_state()", exc_info=True)


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*ViewJob.get_imple())

# endregion Implementation
