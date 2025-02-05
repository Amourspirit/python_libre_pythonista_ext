from typing import Any, cast
import contextlib

from ooodev.calc import CalcDoc
from ooodev.loader.inst.doc_type import DocType

from ..dispatch.calc_sheet_cell_dispatch_provider import CalcSheetCellDispatchProvider
from ..log.log_inst import LogInst
from . import cell_intercept as ci


def register_interceptor(doc_comp: Any) -> None:  # noqa: ANN401
    """
    Registers the dispatch provider interceptor.

    This interceptor will be used to handle the custom .uno: command.

    Args:
        doc (doc_comp): CalcDoc or Uno Calc Component Document.
    """
    if doc_comp is None:
        raise ValueError("doc_comp is None")
    dt = getattr(doc_comp, "DOC_TYPE", None)
    doc = cast(CalcDoc, CalcDoc.get_doc_from_component(doc_comp)) if dt is None else cast(CalcDoc, doc_comp)
    if doc.DOC_TYPE != DocType.CALC:
        raise ValueError("Not a CalcDoc")

    log = None
    with contextlib.suppress(Exception):
        log = LogInst()
        with log.indent(True):
            log.debug("Registering Dispatch Provider Interceptor")

    if CalcSheetCellDispatchProvider.has_instance(doc):
        if log:
            with log.indent(True):
                log.debug("Dispatch Provider Interceptor already registered.")
        return
    inst = CalcSheetCellDispatchProvider(doc)  # singleton
    frame = doc.get_frame()
    frame.registerDispatchProviderInterceptor(inst)  # type: ignore
    view = doc.get_view()
    view.add_event_notify_context_menu_execute(ci.on_menu_intercept)  # type: ignore
    if log:
        with log.indent(True):
            log.debug("Dispatch Provider Interceptor registered.")


def unregister_interceptor(doc_comp: Any) -> None:  # noqa: ANN401
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
        with log.indent(True):
            log.debug("UnRegistering Dispatch Provider Interceptor")

    if not CalcSheetCellDispatchProvider.has_instance(doc):
        if log:
            with log.indent(True):
                log.debug("Dispatch Provider Interceptor was not registered.")
        return
    inst = CalcSheetCellDispatchProvider(doc)  # singleton
    frame = doc.get_frame()
    frame.releaseDispatchProviderInterceptor(inst)  # type: ignore
    view = doc.get_view()
    view.remove_event_notify_context_menu_execute(ci.on_menu_intercept)  # type: ignore
    inst.dispose()  # type: ignore
    if log:
        with log.indent(True):
            log.debug("Dispatch Provider Interceptor unregistered.")
