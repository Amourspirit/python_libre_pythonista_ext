# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
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
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.config import Config
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.const.event_const import DOCUMENT_SAVING
    from ...pythonpath.libre_pythonista_lib.doc_props.calc_props import CalcProps

    # from ...pythonpath.libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
    from ...pythonpath.libre_pythonista_lib.doc.calc_doc_mgr import CalcDocMgr

else:
    override = lambda func: func
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from ___lo_pip___.config import Config
        from libre_pythonista_lib.const.event_const import DOCUMENT_SAVING
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.doc_props.calc_props import CalcProps

        # from libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
        from libre_pythonista_lib.doc.calc_doc_mgr import CalcDocMgr
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
        self._log = self._get_local_logger()

    # endregion Init

    def _update_ext_location(self, doc: CalcDoc):
        cp = CalcProps(doc)
        cp.update_doc_ext_location()

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:
        self._log.debug("execute")
        try:
            # loader = Lo.load_office()
            self._log.debug(f"Args Length: {len(Arguments)}")
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")
            if self.document is None:
                self._log.debug("Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document Saving is a spreadsheet")
                if _CONDITIONS_MET:
                    doc = CalcDoc.get_doc_from_component(self.document)

                    doc_mgr = CalcDocMgr()
                    if not doc_mgr.events_ensured:
                        self._log.debug("Events not ensured. Returning.")
                        return

                    state_mgr = doc_mgr.calc_state_mgr
                    if not state_mgr.is_imports2_ready:
                        self._log.debug("Imports2 is not ready. Returning.")
                        return

                    if not state_mgr.is_pythonista_doc:
                        self._log.debug("Document not currently a LibrePythonista. Returning.")
                        return

                    try:
                        cfg = Config()
                        ver = doc.get_custom_property("LIBRE_PYTHONISTA_VERSION", "")
                        if ver != cfg.extension_version:
                            doc.set_custom_property("LIBRE_PYTHONISTA_VERSION", cfg.extension_version)

                    except Exception as e:
                        self._log.error("Error Setting Custom Properties", exc_info=True)

                    try:
                        self._update_ext_location(doc)
                    except:
                        self._log.error("Error Updating Extension Location", exc_info=True)

                    se = SharedEvent()
                    eargs = EventArgs(self)
                    eargs.event_data = DotDict(doc=doc)
                    se.trigger_event(DOCUMENT_SAVING, eargs)
            else:
                self._log.debug("Document UnLoading not a spreadsheet")

        except Exception as e:
            self._log.error("Error getting current document", exc_info=True)
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
