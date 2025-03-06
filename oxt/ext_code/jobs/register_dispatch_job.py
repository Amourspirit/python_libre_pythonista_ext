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
    _CONDITIONS_MET = True

    # just for design time
    from typing_extensions import override
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from oxt.___lo_pip___.events.lo_events import LoEvents
    from oxt.___lo_pip___.events.args.event_args import EventArgs
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import GET_CURRENT_EVENT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_register_dispatch_interceptor import (
        CmdRegisterDispatchInterceptor,
    )
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ___lo_pip___.events.lo_events import LoEvents
        from ___lo_pip___.events.args.event_args import EventArgs
        from libre_pythonista_lib.doc.doc_globals import GET_CURRENT_EVENT
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_register_dispatch_interceptor import (
            CmdRegisterDispatchInterceptor,
        )
# endregion imports


# region XJob
class RegisterDispatchJob(XJob, unohelper.Base):
    """
    Python UNO Component that implements the com.sun.star.task.Job interface.

    Registers the dispatch interceptor.
    """

    IMPLE_NAME = "___lo_identifier___.RegisterDispatchJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Type[RegisterDispatchJob], str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()
        self._log.debug("init")
        self._log.debug("Conditions met: %s", _CONDITIONS_MET)

        if _CONDITIONS_MET:
            # subscribe to the DocGlobals.get_current event and set the uid for the current document.
            self._fn_on_get_current = self._on_get_current
            self._events = LoEvents()
            self._events.on(GET_CURRENT_EVENT, self._fn_on_get_current)

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # type: ignore  # noqa: ANN401, N803
        self._log.debug("execute")
        try:
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug("Struct: %s", struct.Name)
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")
            if self.document is None:
                self._log.debug("Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document Loading is a spreadsheet")
            else:
                self._log.debug("Document Loading not a spreadsheet")

            if not _CONDITIONS_MET:
                self._log.debug("Conditions not met. Returning.")
                return
            _ = Lo.load_office()
            doc = CalcDoc.get_doc_from_component(self.document)

            cmd_handler = CmdHandlerFactory.get_cmd_handler()
            cmd = CmdRegisterDispatchInterceptor(doc)
            cmd_handler.handle(cmd)

            # no longer needs to listen for the DocGlobals.get_current event.
            self._events.remove(GET_CURRENT_EVENT, self._fn_on_get_current)

        except Exception:
            self._log.exception("Error registering dispatch interceptor")
            return

    # endregion execute

    # region Event Handlers

    def _on_get_current(self, source: Any, event: EventArgs) -> None:  # noqa: ANN401
        if self.document is not None:
            event.event_data["uid"] = self.document.RuntimeUID

    # endregion Event Handlers

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="RegisterDispatchJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*RegisterDispatchJob.get_imple())

# endregion Implementation
