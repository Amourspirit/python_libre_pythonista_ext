# region imports
from __future__ import unicode_literals, annotations
from typing import Any, cast, Tuple, TYPE_CHECKING, Union
import os
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
    from ooodev.events.lo_events import LoEvents
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ooodev.calc import CalcDoc
    from ooodev.loader import Lo
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import (
        CodeSheetModifyListener,
    )
    from oxt.pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
        CodeSheetActivationListener,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lplog import LpLog
    from oxt.pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr
    from oxt.pythonpath.libre_pythonista_lib.menus import cell_reg_interceptor
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING

    # from ...pythonpath.libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc_doc_mgr import CalcDocMgr
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr

    # Initialize the breakpoint manager
    break_mgr = BreakMgr()
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.events.lo_events import LoEvents
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from ooodev.loader import Lo
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import (
            CodeSheetModifyListener,
        )
        from libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
            CodeSheetActivationListener,
        )
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lplog import LpLog
        from libre_pythonista_lib.cell.cell_mgr import CellMgr
        from libre_pythonista_lib.menus import cell_reg_interceptor
        from libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING

        # from libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
        from libre_pythonista_lib.doc.calc_doc_mgr import CalcDocMgr
        from ___lo_pip___.debug.break_mgr import BreakMgr

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        # break_mgr.add_breakpoint("PrepareUnloadJob.execute.conditions_met")
# endregion imports


# region XJob
class PrepareUnloadJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.PrepareUnloadJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[type, str, tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()
        self._doc: Union[CalcDoc, None] = None
        self._fn_on_singleton_get_key = self._on_singleton_get_key
        self._fn_on_doc_event_partial_check_uid = self._on_doc_event_partial_check_uid
        self._fn_on_singleton_get_doc = self._on_singleton_get_doc

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # noqa: ANN401, N803
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
                self._log.debug("Document UnLoading is a spreadsheet")
                key = f"LIBRE_PYTHONISTA_DOC_{self.document.RuntimeUID}"
                if key in os.environ:
                    self._log.debug(f"Removing {key} from os.environ")
                    del os.environ[key]
                else:
                    self._log.debug(f"{key} not found in os.environ")
                if _CONDITIONS_MET:
                    break_mgr.check_breakpoint("PrepareUnloadJob.execute.conditions_met")
                    run_time_id = self.document.RuntimeUID
                    try:
                        from ooodev.calc import CalcDoc

                        self._add_events()

                        self._doc = CalcDoc.get_doc_from_component(self.document)

                        cell_reg_interceptor.unregister_interceptor(self._doc)

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

                        CellMgr.reset_instance(self._doc)
                        view = self._doc.get_view()
                        view.component.addActivationEventListener(CodeSheetActivationListener())
                        for sheet in self._doc.sheets:
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
                    except Exception:
                        self._log.error("Error removing log file", exc_info=True)

                    # many singletons are created and need to be removed
                    # The code.py_source_mgr.PyInstance and many other modules listen for this
                    # event to clean up singletons.
                    se = SharedEvent()
                    event_args = EventArgs(self)
                    event_args.event_data = DotDict(uid=run_time_id, doc=self.document)
                    # LoEvents is used to unload various singletons
                    LoEvents().trigger(GBL_DOC_CLOSING, event_args)

                    event_args.event_data = DotDict(run_id=run_time_id, doc=self.document)
                    se.trigger_event(GBL_DOC_CLOSING, event_args)
                    # any class the has the SingletonBase can be used to clear the instance for the uid
                    CellMgr.remove_instance_by_uid(run_time_id)
            else:
                self._log.debug("Document UnLoading not a spreadsheet")

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return
        finally:
            self._remove_events()

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="PrepareUnloadJob")

    # endregion Logging

    # region Event Add/Remove
    def _add_events(self) -> None:
        events = LoEvents()
        events.remove(
            "LibrePythonistaSingletonGetKey",
            self._fn_on_singleton_get_key,
        )
        events.on(
            "LibrePythonistaSingletonGetKey",
            self._fn_on_singleton_get_key,
        )

        events.remove(
            "LibrePythonistaCodeSheetActivationListenerGetKey",
            self._fn_on_singleton_get_key,
        )
        events.on(
            "LibrePythonistaCodeSheetActivationListenerGetKey",
            self._fn_on_singleton_get_key,
        )

        events.remove(
            "LibrePythonistaCodeSheetModifyListenerGetKey",
            self._fn_on_singleton_get_key,
        )
        events.on(
            "LibrePythonistaCodeSheetModifyListenerGetKey",
            self._fn_on_singleton_get_key,
        )

        events.remove(
            "LibrePythonistaDocEventPartialCheckUid",
            self._fn_on_doc_event_partial_check_uid,
        )
        events.on(
            "LibrePythonistaDocEventPartialCheckUid",
            self._fn_on_doc_event_partial_check_uid,
        )

        events.remove(
            "LibrePythonistaSharedEventGetDoc",
            self._fn_on_singleton_get_doc,
        )
        events.on(
            "LibrePythonistaSharedEventGetDoc",
            self._fn_on_singleton_get_doc,
        )

    def _remove_events(self) -> None:
        events = LoEvents()
        events.remove(
            "LibrePythonistaSingletonGetKey",
            self._fn_on_singleton_get_key,
        )
        events.remove(
            "LibrePythonistaCodeSheetActivationListenerGetKey",
            self._fn_on_singleton_get_key,
        )
        events.remove(
            "LibrePythonistaCodeSheetModifyListenerGetKey",
            self._fn_on_singleton_get_key,
        )
        events.remove(
            "LibrePythonistaDocEventPartialCheckUid",
            self._fn_on_doc_event_partial_check_uid,
        )
        events.remove(
            "LibrePythonistaSharedEventGetDoc",
            self._fn_on_singleton_get_doc,
        )

    # endregion Event Add/Remove

    # region Event Handlers

    def _on_singleton_get_key(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        if self._doc is None:
            return
        event_data = cast(DotDict, event.event_data)
        if event_data.class_name == CalcDocMgr.__name__:
            self._log.debug("CalcDocMgr singleton requested")
            event_data.key = f"{self._doc.runtime_uid}_uid_{CalcDocMgr.__name__}"
        elif event_data.class_name == CellMgr.__name__:
            self._log.debug("CellMgr singleton requested")
            event_data.key = f"{self._doc.runtime_uid}_uid_{CellMgr.__name__}"
        elif event_data.class_name == LpLog.__name__:
            self._log.debug("LpLog singleton requested")
            event_data.key = f"{self._doc.runtime_uid}_uid_{LpLog.__name__}"
        elif event_data.class_name == "CellCache":
            self._log.debug("CellCache singleton requested")
            event_data.key = f"{self._doc.runtime_uid}_uid_CellCache"
        if event_data.class_name == "CodeSheetActivationListener":
            self._log.debug("CodeSheetActivationListener singleton requested")
            event_data.key = f"{self._doc.runtime_uid}_uid"
        if event_data.class_name == "CodeSheetModifyListener":
            self._log.debug("CodeSheetModifyListener singleton requested")
            event_data.key = f"{self._doc.runtime_uid}_uid_{event_data.inst_name}"

    def _on_singleton_get_doc(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        if self._doc is None:
            return
        event_data = cast(DotDict, event.event_data)
        event_data.doc = self._doc

    def _on_doc_event_partial_check_uid(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        if self._doc is None:
            return
        event_data = cast(DotDict, event.event_data)
        event_data.doc_uid = self._doc.runtime_uid

    # endregion Event Handlers


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*PrepareUnloadJob.get_imple())

# endregion Implementation
