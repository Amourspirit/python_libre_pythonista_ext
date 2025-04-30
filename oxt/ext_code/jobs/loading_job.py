# region imports
from __future__ import unicode_literals, annotations
from typing import Any, Type, Tuple, TYPE_CHECKING

import unohelper
import contextlib


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
    from typing_extensions import override
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_calculate_all import CmdCalculateAll
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_init_calculate import CmdInitCalculate
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_calculate_all import CmdCalculateAll
        from libre_pythonista_lib.cq.cmd.doc.cmd_current_ctx_load import CmdCurrentCtxLoad
        from libre_pythonista_lib.cq.qry.doc.qry_is_macro_enabled import QryIsMacroEnabled
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_init_calculate import CmdInitCalculate
        from libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
# endregion imports


# region XJob
class LoadingJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.LoadingJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Type[LoadingJob], str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: object) -> None:
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    def _lo_load(self, doc: Any) -> None:  # noqa: ANN401
        """Loads OooDev"""
        self._log.debug("_lo_load()_ Loading OooDev")
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        cmd = CmdCurrentCtxLoad(ctx=self.ctx, uid=doc.RuntimeUID)
        cmd_handler.handle(cmd)
        if not cmd.success:
            self._log.error("Error loading OooDev")
            return
        self._log.debug("OooDev Loaded")

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # type: ignore  # noqa: ANN401, N803
        self._log.debug("execute")
        try:
            # loader = Lo.load_office()
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")
            if self.document is None:
                self._log.debug("Document is None")
                return

            if _CONDITIONS_MET:
                self._lo_load(self.document)

            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document Loading is a spreadsheet")
                run_id = self.document.RuntimeUID
                doc = CalcDoc.get_doc_from_component(self.document)
                qry_handler = QryHandlerFactory.get_qry_handler()
                cmd_handler = CmdHandlerFactory.get_cmd_handler()

                qry_macro_mode = QryIsMacroEnabled(doc=doc)
                macros_enabled = qry_handler.handle(qry_macro_mode)
                if macros_enabled:
                    self._log.debug("Macros are enabled.")
                else:
                    self._log.debug("Macros are not enabled. Exiting.")
                    return

                qry_calc_all = QryInitCalculate(uid=run_id)
                if qry_handler.handle(qry_calc_all):
                    self._log.debug("Document has been calculated.")
                    return

                self._log.debug("Document has not been calculated.")

                cmd_calc_all = CmdCalculateAll(doc=doc)
                cmd_handler.handle(cmd_calc_all)
                if cmd_calc_all.success:
                    self._log.debug("Successfully calculated all formulas.")
                    cmd_init_calc = CmdInitCalculate(uid=run_id)
                    cmd_handler.handle(cmd_init_calc)
                    if cmd_init_calc.success:
                        self._log.debug("Successfully executed command.")
                    else:
                        self._log.error("Error executing command.")
                else:
                    self._log.error("Error calculating all formulas.")
                return
            else:
                self._log.debug("Document Loading not a spreadsheet")

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="LoadingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*LoadingJob.get_imple())

# endregion Implementation
