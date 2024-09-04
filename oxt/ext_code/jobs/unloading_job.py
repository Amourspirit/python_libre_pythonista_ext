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
    from ooodev.events.lo_events import LoEvents
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from ...pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
        CodeSheetActivationListener,
    )
    from ...pythonpath.libre_pythonista_lib.code.mod_helper.lplog import LpLog
    from ...pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr
    from ...pythonpath.libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
    from ...pythonpath.libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.events.lo_events import LoEvents
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
        from libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
        from libre_pythonista_lib.code.mod_helper.lplog import LpLog
        from libre_pythonista_lib.cell.cell_mgr import CellMgr
        from libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
        from libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING
# endregion imports


# region XJob
class UnLoadingJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.UnLoadingJob"
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

    # region execute
    def execute(self, args: Any) -> None:
        self._log.debug("execute")
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
                self._log.debug("Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document UnLoading is a spreadsheet")
                key = f"LIBRE_PYTHONISTA_DOC_{self.document.RuntimeUID}"
                if key in os.environ:
                    self._log.debug(f"Removing {key} from os.environ")
                    del os.environ[key]
                else:
                    self._log.debug(f"{key} not found in os.environ")
                if _CONDITIONS_MET:
                    run_time_id = self.document.RuntimeUID
                    try:
                        from ooodev.calc import CalcDoc

                        # doc = CalcDoc.from_current_doc()
                        doc = CalcDoc.get_doc_from_component(self.document)
                        dispatch_mgr.unregister_interceptor(doc)
                        CellMgr.reset_instance(doc)
                        view = doc.get_view()
                        view.component.addActivationEventListener(CodeSheetActivationListener())
                        for sheet in doc.sheets:
                            unique_id = sheet.unique_id
                            if CodeSheetModifyListener.has_listener(unique_id):
                                listener = CodeSheetModifyListener(unique_id)  # singleton
                                sheet.component.removeModifyListener(listener)
                    except Exception:
                        self._log.error("Error dispatch manager not unregistered", exc_info=True)
                    try:
                        self._log.debug("Cleaning up LpLog file")
                        if LpLog.has_singleton_instance():
                            lp_log = LpLog()
                            if lp_log.log_path.exists():
                                self._log.debug(f"Removing LpLog file: {lp_log.log_path}")
                                lp_log.log_path.unlink()
                        else:
                            self._log.debug("LpLog instance not found")
                    except Exception as e:
                        self._log.error("Error removing log file", exc_info=True)

                    # many singletons are created and need to be removed
                    # The code.py_source_mgr.PyInstance and many other modules listen for this
                    # event to clean up singletons.
                    se = SharedEvent()
                    event_args = EventArgs(self)
                    event_args.event_data = DotDict(uid=run_time_id, doc=self.document)
                    # TODO: check and see if LoEvents is needed
                    LoEvents().trigger(GBL_DOC_CLOSING, event_args)

                    event_args.event_data = DotDict(run_id=run_time_id, doc=self.document)
                    se.trigger_event(GBL_DOC_CLOSING, event_args)
                    # any class the has the SingletonBase can be used to clear the instance for the uid
                    CellMgr.remove_instance_by_uid(run_time_id)
            else:
                self._log.debug("Document UnLoading not a spreadsheet")

        except Exception as e:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger

        return OxtLogger(log_name="UnLoadingJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*UnLoadingJob.get_imple())

# endregion Implementation
