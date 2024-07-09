from __future__ import unicode_literals, annotations
from typing import cast, TYPE_CHECKING, Tuple
import uno
from ooodev.utils.props import Props
from ooodev.calc import CalcDoc
from ooodev.exceptions import ex as mEx
from ..log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.container import XNameReplace
    from com.sun.star.beans import PropertyValue
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


def set_doc_sheets_calculate_event(doc: CalcDoc):
    cfg = Config()
    log = LogInst()  # singleton
    log.debug("set_doc_sheets_calculate_event()")
    # vnd.sun.star.script:LibrePythonista.oxt|python|scripts|share_event.py$formulas_calc?language=Python&location=user:uno_packages
    new_script = f"vnd.sun.star.script:{cfg.oxt_name}.oxt|python|scripts|{cfg.py_script_sheet_on_calculate}${cfg.macro_sheet_on_calculate}?language=Python&location=user:uno_packages"
    for sheet in doc.sheets:
        events = cast("XNameReplace", sheet.component.getEvents())  # type: ignore
        sheet_name = sheet.name
        if events.hasByName("OnCalculate"):
            # com.sun.star.beans.PropertyValue
            try:
                current_props = cast("Tuple[PropertyValue, ...]", events.getByName("OnCalculate"))
                if current_props:
                    value = Props.get_value("Script", current_props)
                    if value == new_script:
                        log.debug(f"Sheet {sheet_name} already has correct OnCalculate event")
                        continue
            except mEx.PropertyError:
                log.debug(f"set_doc_sheets_calculate_event() - Sheet {sheet_name} - PropertyError Script not found")

            try:
                dict_props = {}
                dict_props["Script"] = new_script
                dict_props["EventType"] = "Script"
                data = Props.make_props(**dict_props)
                uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", data)
                uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))
                log.debug(f"Sheet {sheet_name} - OnCalculate event replaced")
            except Exception:
                log.exception(f"set_doc_sheets_calculate_event() - Sheet {sheet_name}")
        else:
            log.debug(f"Sheet {sheet_name} does not have OnCalculate event")


def remove_doc_sheets_calculate_event(doc: CalcDoc):
    """
    Removes the Script event from the OnCalculate event of the sheets.

    If the document has no Python code added by this extension, then it makes sense to remove the event.
    If the event is not removed then the document will prompt for permission to run the script even if there are no other scripts attached to the document.
    """
    cfg = Config()
    log = LogInst()  # singleton
    log.debug("remove_doc_sheets_calculate_event()")
    new_script = f"vnd.sun.star.script:{cfg.oxt_name}.oxt|python|scripts|{cfg.py_script_sheet_on_calculate}${cfg.macro_sheet_on_calculate}?language=Python&location=user:uno_packages"
    for sheet in doc.sheets:
        events = cast("XNameReplace", sheet.component.getEvents())  # type: ignore
        sheet_name = sheet.name
        if events.hasByName("OnCalculate"):
            # com.sun.star.beans.PropertyValue
            try:
                current_props = cast("Tuple[PropertyValue, ...]", events.getByName("OnCalculate"))
                if current_props:
                    value = Props.get_value("Script", current_props)
                    if value == new_script:
                        # make a empty tuple to remove the event
                        uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", ())
                        uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))
                        continue
            except mEx.PropertyError:
                log.debug(f"remove_doc_sheets_calculate_event() - Sheet {sheet_name} - PropertyError Script not found")
        else:
            log.debug(f"Sheet {sheet_name} does not have OnCalculate event")
