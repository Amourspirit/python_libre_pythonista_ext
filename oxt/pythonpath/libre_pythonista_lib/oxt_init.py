from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ooodev.loader import Lo
from ooodev.calc import CalcDoc
from ooodev.exceptions import ex as mEx
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from .dispatch import dispatch_mgr  # type: ignore
from .state.calc_state_mgr import CalcStateMgr


# from libre_pythonista_lib.sheet.listen.sheet_calculation_event_listener import SheetCalculationEventListener


from .const.event_const import OXT_INIT

if TYPE_CHECKING:
    from ...___lo_pip___.oxt_logger import OxtLogger
else:
    OxtLogger = Any


def oxt_init(document: Any, log: OxtLogger, state_mgr: CalcStateMgr) -> None:
    run_id = document.RuntimeUID

    doc = CalcDoc.get_doc_from_component(document)
    try:
        # Init the CalcStateMgr singleton
        _ = CalcStateMgr(doc)
    except Exception:
        log.error("Error getting CalcStateMgr", exc_info=True)

    if state_mgr.is_imports2_ready:
        log.debug("Imports2 is ready")
        from .doc.listen.document_event_listener import DocumentEventListener
        from .cell.cell_update_mgr import CellUpdateMgr

        try:
            # check to see if the extension location is the same for this instance
            # as the previous time this document was opened.
            # The document may be opened in a different environment,
            # The extension location may be in shared instead of users or vice versa.
            cell_update = CellUpdateMgr(doc)
            cell_update.update_cells()
        except Exception:
            log.error("Error updating cells with CellUpdateMgr", exc_info=True)

        try:
            doc.component.addDocumentEventListener(DocumentEventListener())
            log.debug("Document event listener added")
        except Exception:
            log.error("Error adding document event listener", exc_info=True)
    else:
        log.debug("Imports2 is not ready")

    try:
        view = doc.get_view()
    except mEx.MissingInterfaceError as e:
        log.debug(f"Error getting view from document. {e}")
        view = None
    if view is None:
        log.debug("View is None. May be print preview. Returning.")
        return

    if not view.view_controller_name == "Default":
        # this could mean that the print preview has been activated.
        # Print Preview view controller Name: PrintPreview
        log.debug(f"'{view.view_controller_name}' is not the default view controller. Returning.")
        return

    if state_mgr.is_imports2_ready:
        from .sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
        from .sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
        from .sheet.listen.sheet_activation_listener import SheetActivationListener

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
        sheet_act_listener = SheetActivationListener()
        view.component.removeActivationEventListener(code_sheet_activation_listener)
        view.component.addActivationEventListener(code_sheet_activation_listener)
        view.component.removeActivationEventListener(sheet_act_listener)
        view.component.addActivationEventListener(sheet_act_listener)

        if view.is_form_design_mode():
            try:
                log.debug("Setting form design mode to False")
                view.set_form_design_mode(False)
                log.debug("Form design mode set to False")
                # doc.toggle_design_mode()
            except Exception:
                log.warning("Unable to set form design mode", exc_info=True)

    # Can still register the dispatch manager even if the imports are not ready.
    log.debug(f"Pre Dispatch manager loaded, UID: {doc.runtime_uid}")
    dispatch_mgr.unregister_interceptor(doc)
    dispatch_mgr.register_interceptor(doc)

    if state_mgr.is_imports2_ready:
        from .event.shared_event import SharedEvent
        from .sheet.sheet_mgr import SheetMgr
        from .cell.cell_mgr import CellMgr  # type: ignore

        _ = SheetMgr(doc)  # init the singleton

        cm = CellMgr(doc)
        cm.reset_py_inst()
        cm.add_all_listeners()

        document.calculateAll()
        se = SharedEvent()
        eargs = EventArgs(object())
        eargs.event_data = DotDict(run_id=run_id, doc=doc, event=OXT_INIT, doc_type=doc.DOC_TYPE)
        se.trigger_event(OXT_INIT, eargs)
