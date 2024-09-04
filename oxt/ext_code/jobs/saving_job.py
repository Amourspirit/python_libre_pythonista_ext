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
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...___lo_pip___.config import Config
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.const.event_const import DOCUMENT_SAVING
    from ...pythonpath.libre_pythonista_lib.doc_props.calc_props import CalcProps

else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from ___lo_pip___.config import Config
        from libre_pythonista_lib.const.event_const import DOCUMENT_SAVING
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.doc_props.calc_props import CalcProps
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

    def _update_ext_location(self, doc: CalcDoc):
        cp = CalcProps(doc)
        cp.update_doc_ext_location()

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
                        self._update_ext_location(doc)
                    except:
                        self._logger.error("Error Updating Extension Location", exc_info=True)

                    se = SharedEvent()
                    eargs = EventArgs(self)
                    eargs.event_data = DotDict(doc=doc)
                    # SheetMgr will remove any unused Formula Calculate events from the sheets.
                    se.trigger_event(DOCUMENT_SAVING, eargs)
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
