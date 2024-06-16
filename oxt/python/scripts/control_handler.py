from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import uno
from com.sun.star.awt import Rectangle
from ooodev.calc import CalcDoc, CalcCell
from ooodev.form.controls.from_control_factory import FormControlFactory

if TYPE_CHECKING:
    from com.sun.star.script.provider import XScriptContext
    from com.sun.star.awt import ActionEvent
    from com.sun.star.drawing import ControlShape  # service

    from ...pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from ...pythonpath.libre_pythonista_lib.cell.menu.ctl_popup import CtlPopup

    XSCRIPTCONTEXT: XScriptContext
else:
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.cell.menu.ctl_popup import CtlPopup


def on_btn_action_preformed(*args):
    """
    Handle the button action event.
    """
    if not args:
        return

    log = LogInst()
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
        log.debug(f"button_handler: calc_doc: {calc_doc.runtime_uid}")

        sheet = calc_doc.sheets.get_active_sheet()
        factory = FormControlFactory(draw_page=sheet.draw_page.component, lo_inst=calc_doc.lo_inst)
        shape = cast("ControlShape", factory.find_shape_for_control(ev_obj.Source.Model))  # type: ignore
        # the anchor for the control shape is the cell
        x_cell = shape.Anchor  # type: ignore

        cell_obj = calc_doc.range_converter.get_cell_obj(x_cell)
        calc_cell = sheet[cell_obj]
        # get a CellOjb instance that is easier to work with
        log.debug(f"button_handler: cell_obj: {cell_obj}")

        ctl_pop = CtlPopup(cell=calc_cell)
        pm = ctl_pop.get_menu()
        pm.execute(ev_obj.Source.getContext().getPeer(), ev_obj.Source.getPosSize(), 0)  # type: ignore

    except Exception:
        log.error("button_handler: Error", exc_info=True)


# args[0] is the event object
#  - libre_pythonista - DEBUG - button_handler: arg:
# (com.sun.star.awt.ActionEvent){ (com.sun.star.lang.EventObject)
# { Source = (com.sun.star.uno.XInterface)0x7f976d4a9ee0
# {implementationName=com.sun.star.form.OButtonControl,
# supportedServices={com.sun.star.awt.UnoControl,
# com.sun.star.awt.UnoControlButton,
# stardiv.vcl.control.Button,
# com.sun.star.form.control.SubmitButton,
# com.sun.star.form.control.CommandButton,
# stardiv.one.form.control.CommandButton},
# supportedInterfaces={com.sun.star.accessibility.XAccessible,
# com.sun.star.awt.XActionListener,
# com.sun.star.awt.XButton,com.sun.star.awt.XControl,
# com.sun.star.awt.XItemListener,
# com.sun.star.awt.XLayoutConstrains,
# com.sun.star.awt.XStyleSettingsSupplier,
# com.sun.star.awt.XToggleButton,
# com.sun.star.awt.XUnitConversion,
# com.sun.star.awt.XView,com.sun.star.awt.XWindow2,
# com.sun.star.beans.XPropertiesChangeListener,
# com.sun.star.beans.XPropertyChangeListener,
# com.sun.star.form.XApproveActionBroadcaster,
# com.sun.star.form.submission.XSubmission,
# com.sun.star.frame.XDispatchProviderInterception,
# com.sun.star.frame.XStatusListener,
# com.sun.star.lang.XComponent,
# com.sun.star.lang.XEventListener,
# com.sun.star.lang.XServiceInfo,
# com.sun.star.lang.XTypeProvider,
# com.sun.star.uno.XAggregation,
# com.sun.star.uno.XWeak,
# com.sun.star.util.XModeChangeBroadcaster}} },
# ActionCommand = (string)"" }


g_exportedScripts = (on_btn_action_preformed,)
