"""To rename this module, change the module name in the project.toml ``tool.libre_pythonista.config.py_script_sheet_ctl_click`` and the filename."""

from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import uno
from ooodev.calc import CalcDoc
from ooodev.form.controls.from_control_factory import FormControlFactory

if TYPE_CHECKING:
    from com.sun.star.script.provider import XScriptContext
    from com.sun.star.awt import ActionEvent
    from com.sun.star.drawing import ControlShape  # service

    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.menus.ctl_popup import CtlPopup

    XSCRIPTCONTEXT: XScriptContext
else:
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.doc.calc.doc.menus.ctl_popup import CtlPopup


def on_btn_action_preformed(*args: Any) -> None:  # noqa: ANN401
    """
    Handle the button action event.
    """
    log = LogInst()
    if not args:
        log.debug("button_handler: No args. Returning.")
        return

    log.debug("button_handler debug")
    ev_obj: ActionEvent = args[0]
    action_command = getattr(ev_obj, "ActionCommand", None)
    if action_command is None:
        log.error("button_handler: ActionCommand not found. Not a valid ActionEvent")
        return
    try:
        doc = XSCRIPTCONTEXT.getDocument()
        if doc is None:
            log.error("button_handler: Document not found")
            return
        if not doc.supportsService("com.sun.star.sheet.SpreadsheetDocument"):  # type: ignore
            log.error("button_handler: Document is not a spreadsheet document")
        calc_doc = CalcDoc.get_doc_from_component(doc)
        log.debug("button_handler: calc_doc: %s", calc_doc.runtime_uid)

        sheet = calc_doc.sheets.get_active_sheet()
        factory = FormControlFactory(draw_page=sheet.draw_page.component, lo_inst=calc_doc.lo_inst)
        shape = cast("ControlShape", factory.find_shape_for_control(ev_obj.Source.Model))  # type: ignore
        # the anchor for the control shape is the cell
        x_cell = shape.Anchor  # type: ignore

        cell_obj = calc_doc.range_converter.get_cell_obj(x_cell)
        calc_cell = sheet[cell_obj]
        # get a CellOjb instance that is easier to work with
        log.debug("button_handler: cell_obj: %s", cell_obj)

        ctl_pop = CtlPopup(cell=calc_cell)
        pm = ctl_pop.get_menu()
        pm.execute(ev_obj.Source.getContext().getPeer(), ev_obj.Source.getPosSize(), 0)  # type: ignore
        log.debug("button_handler: Menu executed")

    except Exception:
        log.error("button_handler: Error", exc_info=True)


g_exportedScripts = (on_btn_action_preformed,)  # noqa: N816
