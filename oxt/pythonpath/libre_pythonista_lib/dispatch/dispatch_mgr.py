#!/usr/bin/env python
from typing import Any, cast, TYPE_CHECKING
import re
import contextlib
import uno
from ooo.dyn.ui.context_menu_interceptor_action import (
    ContextMenuInterceptorAction as ContextMenuAction,
)
from ooodev.adapter.ui.context_menu_interceptor import ContextMenuInterceptor
from ooodev.adapter.ui.context_menu_interceptor_event_data import (
    ContextMenuInterceptorEventData,
)
from ooodev.calc import CalcDoc, CalcSheetView
from ooodev.events.args.event_args_generic import EventArgsGeneric
from ooodev.gui.menu.context.action_trigger_item import ActionTriggerItem
from ooodev.gui.menu.context.action_trigger_sep import ActionTriggerSep
from ooodev.loader.inst.doc_type import DocType
from .dispatch_provider_interceptor import DispatchProviderInterceptor
from ..log.log_inst import LogInst
from ..res.res_resolver import ResResolver


if TYPE_CHECKING:
    from com.sun.star.table import CellAddress


def on_menu_intercept(
    src: ContextMenuInterceptor,
    event: EventArgsGeneric[ContextMenuInterceptorEventData],
    view: CalcSheetView,
) -> None:
    """Event Listener for the context menu intercept."""
    with contextlib.suppress(Exception):
        # don't block other menus if there is an issue.

        container = event.event_data.event.action_trigger_container

        # The default action is ContextMenuAction.IGNORED.
        # In Linux as least (Ubuntu 20.04) the default will crash LibreOffice.
        # This is not the case in Windows, so this seems to be a bug.
        # Setting the action to ContextMenuAction.CONTINUE_MODIFIED will prevent the crash and
        # all seems to work well.
        event.event_data.action = ContextMenuAction.CONTINUE_MODIFIED

        # check the first and last items in the container
        if container[0].CommandURL == ".uno:Cut" and container[-1].CommandURL == ".uno:FormatCellDialog":
            # get the current selection
            selection = event.event_data.event.selection.get_selection()

            if selection.getImplementationName() == "ScCellObj":
                # current selection is a cell.

                log = LogInst()
                addr = cast("CellAddress", selection.getCellAddress())
                doc = CalcDoc.from_current_doc()
                sheet = doc.get_active_sheet()
                cell_obj = doc.range_converter.get_cell_obj_from_addr(addr)
                cell = sheet[cell_obj]
                if not cell.has_custom_property("libre_pythonista_codename"):
                    log.debug(f"Cell {cell_obj} does not have libre_pythonista_codename custom property.")
                    return

                # insert a new menu item.
                # it's command is a custom .uno: command. Note that the command is not a built-in command.
                # The command also contains args for the sheet and cell.
                # A custom dispatch interceptor will be used to handle the command.
                try:
                    log.debug("Getting Resource for mnuEditCode")
                    edit_mnu = ResResolver().resolve_string("mnuEditCode")

                    container.insert_by_index(4, ActionTriggerItem(f".uno:libre_pythonista.calc.menu.code.edit?sheet={sheet.name}&cell={cell_obj}", edit_mnu))  # type: ignore
                    # container.insert_by_index(4, ActionTriggerItem(f".uno:libre_pythonista.calc.menu.reset.orig?sheet={sheet.name}&cell={cell_obj}", "Rest to Original"))  # type: ignore
                    container.insert_by_index(4, ActionTriggerSep())  # type: ignore
                    event.event_data.action = ContextMenuAction.CONTINUE_MODIFIED
                except Exception:
                    log.error("Error inserting context menu item.", exc_info=True)


def register_interceptor(doc_comp: Any):
    """
    Registers the dispatch provider interceptor.

    This interceptor will be used to handle the custom .uno: command.

    Args:
        doc (doc_comp): CalcDoc or Uno Calc Component Document.
    """
    if doc_comp is None:
        raise ValueError("doc_comp is None")
    dt = getattr(doc_comp, "DOC_TYPE", None)
    if dt is None:
        # logger.debug(CalcDoc.DOC_TYPE.get_service())
        # logger.debug(f"Is Doc Type {Info.is_doc_type(doc_comp, CalcDoc.DOC_TYPE.get_service())}")
        doc = cast(CalcDoc, CalcDoc.get_doc_from_component(doc_comp))  # type: ignore
    else:
        doc = cast(CalcDoc, doc_comp)
    if doc.DOC_TYPE != DocType.CALC:
        raise ValueError("Not a CalcDoc")

    log = None
    with contextlib.suppress(Exception):
        log = LogInst()
        log.debug("Registering Dispatch Provider Interceptor")

    if DispatchProviderInterceptor.has_instance(doc):
        if log:
            log.debug("Dispatch Provider Interceptor already registered.")
        return
    inst = DispatchProviderInterceptor(doc)  # singleton
    frame = doc.get_frame()
    frame.registerDispatchProviderInterceptor(inst)
    view = doc.get_view()
    view.add_event_notify_context_menu_execute(on_menu_intercept)
    if log:
        log.debug("Dispatch Provider Interceptor registered.")


def unregister_interceptor(doc_comp: Any):
    """
    Un-registers the dispatch provider interceptor.

    Args:
        doc (doc_comp): CalcDoc or Uno Calc Component Document.
    """
    if doc_comp is None:
        raise ValueError("doc_comp is None")
    dt = getattr(doc_comp, "DOC_TYPE", None)
    if dt is None:
        CalcDoc.DOC_TYPE.get_service()
        doc = cast(CalcDoc, CalcDoc.get_doc_from_component(doc_comp))  # type: ignore
    else:
        doc = cast(CalcDoc, doc_comp)
    if doc.DOC_TYPE != DocType.CALC:
        raise ValueError("Not a CalcDoc")
    log = None
    with contextlib.suppress(Exception):
        log = LogInst()
        log.debug("UnRegistering Dispatch Provider Interceptor")

    if not DispatchProviderInterceptor.has_instance(doc):
        if log:
            log.debug("Dispatch Provider Interceptor was not registered.")
        return
    inst = DispatchProviderInterceptor(doc)  # singleton
    frame = doc.get_frame()
    frame.releaseDispatchProviderInterceptor(inst)
    view = doc.get_view()
    view.remove_event_notify_context_menu_execute(on_menu_intercept)
    inst.dispose()
    if log:
        log.debug("Dispatch Provider Interceptor unregistered.")
