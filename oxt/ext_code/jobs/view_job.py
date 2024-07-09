# region imports
from __future__ import unicode_literals, annotations
from typing import Any, TYPE_CHECKING
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
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ooodev.loader import Lo
    from ooodev.exceptions import ex as mEx
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
    from ...pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr  # type: ignore
    from ...pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from ...pythonpath.libre_pythonista_lib.const.event_const import CB_DOC_FOCUS_GAINED, DOCUMENT_NEW_VIEW
    from ...pythonpath.libre_pythonista_lib.sheet.calculate import set_doc_sheets_calculate_event
    from ...pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
        CodeSheetActivationListener,
    )
    from ...pythonpath.libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import (
        SheetCalculationEventListener,
    )

    # from ...pythonpath.libre_pythonista_lib.doc.listen.document_event_listener import DocumentEventListener
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.exceptions import ex as mEx
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.dispatch import dispatch_mgr  # type: ignore
        from libre_pythonista_lib.cell.cell_mgr import CellMgr  # type: ignore
        from libre_pythonista_lib.sheet.calculate import set_doc_sheets_calculate_event
        from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
        from libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
        from libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import SheetCalculationEventListener

        # from libre_pythonista_lib.doc.listen.document_event_listener import DocumentEventListener
        from libre_pythonista_lib.const.event_const import CB_DOC_FOCUS_GAINED, DOCUMENT_NEW_VIEW
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
                        # Because print preview is a different view controller it can cause issues
                        # when the document is put into print preview.
                        # When print preview is opened and is closed this method fires.
                        # Checking for com.sun.star.sheet.XSpreadsheetView via the qi() method,
                        # which is what OooDev does when it is getting the view,
                        # is a good way to check if the view is the default view controller.
                        # Removing all listeners and adding them again seems to work.
                        # If this is not done the dispatch manager will not work correctly.
                        # Specifically the intercept menu's stop working after print preview is closed.
                        self._log.debug("Registering dispatch manager")
                        from ooodev.calc import CalcDoc

                        # Lo.load_office() only loads office if it is not already loaded
                        # It is needed here or the dispatch manager will not receive the correct document
                        # when multiple documents are open.
                        _ = Lo.load_office()
                        doc = CalcDoc.get_doc_from_component(self.document)
                        try:
                            set_doc_sheets_calculate_event(doc)
                        except Exception:
                            self._log.error("Error setting document sheets calculate event", exc_info=True)
                        # try:
                        #     doc.component.addDocumentEventListener(DocumentEventListener())
                        #     self._log.debug("Document event listener added")
                        # except Exception:
                        #     self._log.error("Error adding document event listener", exc_info=True)
                        try:
                            view = doc.get_view()
                        except mEx.MissingInterfaceError as e:
                            self._log.debug(f"Error getting view from document. {e}")
                            view = None
                        if view is None:
                            self._log.debug("View is None. May be print preview. Returning.")
                            return
                        if not view.view_controller_name == "Default":
                            # this could mean that the print preview has been activated.
                            # Print Preview view controller Name: PrintPreview
                            self._log.debug(
                                f"'{view.view_controller_name}' is not the default view controller. Returning."
                            )
                            return

                        for sheet in doc.sheets:
                            unique_id = sheet.unique_id
                            if not CodeSheetModifyListener.has_listener(unique_id):
                                listener = CodeSheetModifyListener(unique_id)  # singleton
                                sheet.component.addModifyListener(listener)
                            else:
                                listener = CodeSheetModifyListener.get_listener(unique_id)  # singleton
                                sheet.component.removeModifyListener(listener)
                                sheet.component.addModifyListener(listener)

                        # adds new modifier listeners to new sheets
                        code_sheet_activation_listener = CodeSheetActivationListener()
                        # add calculate event to new sheets
                        sheet_calc_event_listener = SheetCalculationEventListener()
                        view.component.removeActivationEventListener(code_sheet_activation_listener)
                        view.component.addActivationEventListener(code_sheet_activation_listener)
                        view.component.addActivationEventListener(sheet_calc_event_listener)
                        if view.is_form_design_mode():

                            try:
                                self._log.debug("Setting form design mode to False")
                                view.set_form_design_mode(False)
                                self._log.debug("Form design mode set to False")
                                # doc.toggle_design_mode()
                            except Exception:
                                self._log.warning("Unable to set form design mode", exc_info=True)

                        self._log.debug(f"Pre Dispatch manager loaded, UID: {doc.runtime_uid}")
                        dispatch_mgr.unregister_interceptor(doc)
                        dispatch_mgr.register_interceptor(doc)
                        cm = CellMgr(doc)
                        cm.reset_py_inst()
                        # cm.remove_all_listeners()
                        # adding listeners will remove first.
                        cm.add_all_listeners()

                        self.document.calculateAll()
                        se = SharedEvent()
                        eargs = EventArgs(self)
                        eargs.event_data = DotDict(run_id=run_id, doc=doc, event="new_view", doc_type=doc.DOC_TYPE)
                        se.trigger_event(DOCUMENT_NEW_VIEW, eargs)
                    except Exception:
                        self._log.error("Error setting components on view.", exc_info=True)
                else:
                    self._log.debug("Conditions not met to register dispatch manager")
                self._log.debug("Dispatch manager registered")
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


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*ViewJob.get_imple())

# endregion Implementation
