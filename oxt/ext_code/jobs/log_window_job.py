# region imports
from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING
import contextlib
import unohelper


from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ooodev.calc import CalcDoc
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
    from oxt.pythonpath.libre_pythonista_lib.const.res_const import RES_LOG_WIN_URL
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import (
        LOG_OPTIONS_CHANGED,
        LOG_PY_LOGGER_RESET,
    )
else:
    override = lambda func: func  # noqa: E731
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
        from libre_pythonista_lib.const.res_const import RES_LOG_WIN_URL
        from libre_pythonista_lib.const.event_const import (
            LOG_OPTIONS_CHANGED,
            LOG_PY_LOGGER_RESET,
        )  # noqa: F401
    else:
        RES_LOG_WIN_URL = ""
# endregion imports


# region XJob
class LogWindowJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.LogWindowJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return cls, cls.IMPLE_NAME, cls.SERVICE_NAMES

    # region Init

    def __init__(self, ctx: object) -> None:
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # noqa: ANN401, N803
        # print("LibrePythonistaLogWindowJob execute")
        global RES_LOG_WIN_URL
        self._log.debug("execute")
        if not _CONDITIONS_MET:
            self._log.debug("Conditions not met. Returning.")
            return

        try:
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug("Struct: %s", struct.Name)
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")

            if self.document is None:
                self._log.debug("ViewJob - Document is None")
                return

            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document is a spreadsheet")
                qry_handler = QryHandlerFactory.get_qry_handler()
                doc = CalcDoc.get_doc_from_component(self.document)
                qry_macro_mode = QryIsMacroEnabled(doc=doc)
                macros_enabled = qry_handler.handle(qry_macro_mode)
                if macros_enabled:
                    self._log.debug("Macros are enabled.")
                else:
                    self._log.debug("Macros are not enabled. Exiting.")
                    return

                layout_mgr = self.document.getCurrentController().getFrame().LayoutManager
                if layout_mgr.isElementVisible(RES_LOG_WIN_URL):
                    layout_mgr.hideElement(RES_LOG_WIN_URL)
                self._log.debug("Log Window Job Done")
            else:
                self._log.debug("Document is not a spreadsheet")
                return

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="LogWindowJob")

    # endregion Logging


# endregion XJob


# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*LogWindowJob.get_imple())

# endregion Implementation
