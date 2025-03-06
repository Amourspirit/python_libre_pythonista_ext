# region imports
from __future__ import unicode_literals, annotations
from typing import Any, Tuple, Type, TYPE_CHECKING
import contextlib

import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    from typing_extensions import override

    # just for design time
    _CONDITIONS_MET = True
    from ooodev.calc import CalcDoc
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from oxt.___lo_pip___.events.lo_events import LoEvents
    from oxt.___lo_pip___.events.args.event_args import EventArgs
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import DOCUMENT_SAVING
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import GET_CURRENT_EVENT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_lp_version import CmdLpVersion
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_import2_available import QryIsImport2Available
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_init import QryDocInit
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_calc_props import QryCalcProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_lp_version import QryLpVersion
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.ext.qry_ext_version import QryExtVersion
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.ext.qry_ext_location import QryExtLocation
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps

else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from ___lo_pip___.events.lo_events import LoEvents
        from ___lo_pip___.events.args.event_args import EventArgs
        from libre_pythonista_lib.const.event_const import DOCUMENT_SAVING
        from libre_pythonista_lib.doc.doc_globals import GET_CURRENT_EVENT
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

        # from libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
        from libre_pythonista_lib.cq.cmd.doc.cmd_lp_version import CmdLpVersion
        from libre_pythonista_lib.cq.qry.general.qry_is_import2_available import QryIsImport2Available
        from libre_pythonista_lib.cq.qry.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
        from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_init import QryDocInit
        from libre_pythonista_lib.cq.qry.calc.doc.qry_calc_props import QryCalcProps
        from libre_pythonista_lib.cq.qry.doc.qry_lp_version import QryLpVersion
        from libre_pythonista_lib.cq.qry.doc.ext.qry_ext_version import QryExtVersion
        from libre_pythonista_lib.cq.qry.doc.ext.qry_ext_location import QryExtLocation
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
# endregion imports


# region XJob
class SavingJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.SavingJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Type[SavingJob], str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

        if _CONDITIONS_MET:
            # subscribe to the DocGlobals.get_current event and set the uid for the current document.
            self._fn_on_get_current = self._on_get_current
            self._events = LoEvents()
            self._events.on(GET_CURRENT_EVENT, self._fn_on_get_current)

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # noqa: ANN401, N803
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
                self._log.debug("Document Saving is a spreadsheet")
                if _CONDITIONS_MET:
                    qry_handler = QryHandlerFactory.get_qry_handler()
                    qry = QryIsImport2Available()
                    if not qry_handler.handle(qry):
                        self._log.debug("Imports2 is not available. Returning.")
                        return

                    doc = CalcDoc.get_doc_from_component(self.document)

                    qry_is_doc_pythonista = QryIsDocPythonista(doc)
                    if not qry_handler.handle(qry_is_doc_pythonista):
                        self._log.debug("Document is not a LibrePythonista. Returning.")
                        return

                    qry_doc_init = QryDocInit()
                    if not qry_handler.handle(qry_doc_init):
                        self._log.debug("Document is not initialized. Returning.")
                        return

                    try:
                        qry_ext_version = QryExtVersion()
                        qry_lp_version = QryLpVersion(doc)
                        ext_version = qry_handler.handle(qry_ext_version)
                        lp_version = qry_handler.handle(qry_lp_version)

                        if lp_version is None or lp_version != ext_version:
                            self._log.debug("Extension version is not current. Setting.")
                            cmd_lp_version = CmdLpVersion(doc=doc)
                            cmd_handler = CmdHandlerFactory.get_cmd_handler()
                            cmd_handler.handle(cmd_lp_version)

                    except Exception:
                        self._log.error("Error Setting Custom Properties", exc_info=True)

                    try:
                        qry_ext_location = QryExtLocation()
                        ext_location = qry_handler.handle(qry_ext_location)
                        qry_props = QryCalcProps(doc)
                        props = qry_handler.handle(qry_props)
                        props.doc_ext_location = ext_location
                        if props.is_modified:
                            cmd_props = CmdLpDocProps(doc=doc, props=props.to_dict())
                            cmd_handler = CmdHandlerFactory.get_cmd_handler()
                            cmd_handler.handle(cmd_props)

                    except Exception:
                        self._log.error("Error Updating Extension Location", exc_info=True)

                    se = SharedEvent()
                    eargs = EventArgs(self)
                    eargs.event_data = DotDict(doc=doc)
                    se.trigger_event(DOCUMENT_SAVING, eargs)

                    # no longer needs to listen for the DocGlobals.get_current event.
                    self._events.remove(GET_CURRENT_EVENT, self._fn_on_get_current)
            else:
                self._log.debug("Document UnLoading not a spreadsheet")

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
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

        return OxtLogger(log_name="SavingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*SavingJob.get_imple())

# endregion Implementation
