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
    from ooodev.loader import Lo
    from ooodev.events.args.event_args import EventArgs
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.config import Config
    from ...pythonpath.libre_pythonista_lib.const.res_const import RES_LOG_WIN_URL
    from ...pythonpath.libre_pythonista_lib.const.event_const import LOG_OPTIONS_CHANGED, LOG_PY_LOGGER_RESET
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.events.args.event_args import EventArgs
        from ___lo_pip___.config import Config
        from libre_pythonista_lib.const.res_const import RES_LOG_WIN_URL
        from libre_pythonista_lib.const.event_const import LOG_OPTIONS_CHANGED, LOG_PY_LOGGER_RESET
        from libre_pythonista_lib.event.shared_event import SharedEvent
    else:
        RES_LOG_WIN_URL = ""
# endregion imports


# region XJob
class LogWindowJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.LogWindowJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls):
        return cls, cls.IMPLE_NAME, cls.SERVICE_NAMES

    # region Init

    def __init__(self, ctx):
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._logger = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:  # type: ignore
        # print("LibrePythonistaLogWindowJob execute")
        global RES_LOG_WIN_URL
        self._logger.debug("execute")
        try:
            # can't use args here because this job is also called via dispatch
            # loader = Lo.load_office()
            self._logger.debug(f"Args Length: {len(args)}")

            doc = Lo.current_doc
            if not doc:
                self._logger.debug("Document is None")
                return
            document = doc.component  # type: ignore
            if document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._logger.debug("Document is a spreadsheet")
            else:
                self._logger.debug("Document is not a spreadsheet")
                return
            if _CONDITIONS_MET:
                try:
                    # Lo.dispatch_cmd(cmd="service:___lo_identifier___.Switcher", in_thread=True)
                    layout_mgr = document.getCurrentController().getFrame().LayoutManager
                    if layout_mgr.isElementVisible(RES_LOG_WIN_URL):
                        layout_mgr.hideElement(RES_LOG_WIN_URL)
                    # SharedEvent().trigger_event(LOG_OPTIONS_CHANGED, EventArgs(self))
                    self._logger.debug("Log Window Job Done")

                except Exception as e:
                    self._logger.error("Error Setting Custom Properties", exc_info=True)

        except Exception as e:
            self._logger.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="LogWindowJob")

    # endregion Logging


# endregion XJob


# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*LogWindowJob.get_imple())

# endregion Implementation
