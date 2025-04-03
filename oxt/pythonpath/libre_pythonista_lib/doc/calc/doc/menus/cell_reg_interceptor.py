from typing import Any, cast, TYPE_CHECKING
import contextlib

from ooodev.calc import CalcDoc
from ooodev.loader.inst.doc_type import DocType
from ooodev.exceptions import ex as mEx  # noqa: N812


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.menus import cell_intercept as ci
    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from oxt.pythonpath.libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import (
        CalcSheetCellDispatchProvider,
    )
else:
    from libre_pythonista_lib.doc.calc.doc.menus import cell_intercept as ci
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import CalcSheetCellDispatchProvider


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
        log.debug("Registering Dispatch Provider Interceptor")

    if CalcSheetCellDispatchProvider.has_instance(doc):
        if log:
            log.debug("Dispatch Provider Interceptor already registered.")
        return
    view = doc.get_view()  # get view early just in case it is not a Calc view
    inst = CalcSheetCellDispatchProvider(doc)  # singleton
    frame = doc.get_frame()
    frame.registerDispatchProviderInterceptor(inst)  # type: ignore
    view.add_event_notify_context_menu_execute(ci.on_menu_intercept)  # type: ignore
    if log:
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
        log.debug("UnRegistering Dispatch Provider Interceptor")

    if not CalcSheetCellDispatchProvider.has_instance(doc):
        if log:
            log.debug("Dispatch Provider Interceptor was not registered.")
        return
    inst = CalcSheetCellDispatchProvider(doc)  # singleton
    try:
        frame = doc.get_frame()
        frame.releaseDispatchProviderInterceptor(inst)  # type: ignore
        view = doc.get_view()
        view.remove_event_notify_context_menu_execute(ci.on_menu_intercept)  # type: ignore
    except mEx.MissingInterfaceError as e:
        if log:
            log.debug("View is not a Calc view: %s", e)
        return
    inst.dispose()  # type: ignore
    if log:
        log.debug("Dispatch Provider Interceptor unregistered.")
