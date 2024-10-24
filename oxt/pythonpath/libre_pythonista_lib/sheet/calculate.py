from __future__ import unicode_literals, annotations
from typing import cast, TYPE_CHECKING, Tuple
import uno
from ooodev.utils.props import Props
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.exceptions import ex as mEx
from ..log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.container import XNameReplace
    from com.sun.star.beans import PropertyValue
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


def _get_new_script() -> str:
    cfg = Config()
    if cfg.is_shared_installed:
        location = "share:uno_packages"
    else:
        location = "user:uno_packages"

    return f"vnd.sun.star.script:{cfg.oxt_name}.oxt|python|scripts|{cfg.py_script_sheet_on_calculate}${cfg.macro_sheet_on_calculate}?language=Python&location={location}"


def sheet_has_calculate_event(sheet: CalcSheet) -> bool:
    """
    Check if the sheet has the specified event.
    """
    events = cast("XNameReplace", sheet.component.getEvents())  # type: ignore
    if events.hasByName("OnCalculate"):
        try:
            current_props = cast("Tuple[PropertyValue, ...]", events.getByName("OnCalculate"))
            if current_props:
                new_script = _get_new_script()
                value = Props.get_value("Script", current_props)
                return value == new_script
        except Exception:
            log = LogInst()
            log.exception(f"calculate.sheet_has_calculate_event() - Sheet {sheet.name}")

    return False


def set_sheet_calculate_event(sheet: CalcSheet):
    log = LogInst()  # singleton
    log.debug("calculate.set_sheet_calculate_event()")
    events = cast("XNameReplace", sheet.component.getEvents())  # type: ignore
    if events.hasByName("OnCalculate"):
        try:
            new_script = _get_new_script()
            try:
                dict_props = {}
                dict_props["Script"] = new_script
                dict_props["EventType"] = "Script"
                data = Props.make_props(**dict_props)
                uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", data)  # type: ignore
                uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))  # type: ignore
                log.debug(f"calculate.set_sheet_calculate_event() Sheet {sheet.name} - OnCalculate event replaced")
            except Exception:
                log.exception(f"set_doc_sheets_calculate_event() - Sheet {sheet.name}")

        except Exception:
            log.exception(f"calculate.set_sheet_calculate_event() - Sheet {sheet.name}")
    else:
        log.debug(f"calculate.set_sheet_calculate_event() Sheet {sheet.name} does not have OnCalculate event")


def set_doc_sheets_calculate_event(doc: CalcDoc):
    """
    Set the OnCalculate event for all sheets in the document.
    Unless the current event is the same as the new event it will be replaced.

    Args:
        doc (CalcDoc): CalcDoc instance

    Note:
        It is possible that this sheet could be loaded into two different instances of CalcDoc with the same
        version of the extension installed. On may be installed the Shared version and the other the User version.
        In this case the events will be replaced with the correct version of the script.
    """
    log = LogInst()  # singleton
    log.debug("calculate.set_doc_sheets_calculate_event()")
    # vnd.sun.star.script:LibrePythonista.oxt|python|scripts|share_event.py$formulas_calc?language=Python&location=user:uno_packages
    new_script = _get_new_script()
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
                log.debug(
                    f"calculate.set_doc_sheets_calculate_event() - Sheet {sheet_name} - PropertyError Script not found"
                )

            try:
                dict_props = {}
                dict_props["Script"] = new_script
                dict_props["EventType"] = "Script"
                data = Props.make_props(**dict_props)
                uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", data)  # type: ignore
                uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))  # type: ignore
                log.debug(
                    f"calculate.set_doc_sheets_calculate_event() Sheet {sheet_name} - OnCalculate event replaced"
                )
            except Exception:
                log.exception(f"calculate.set_doc_sheets_calculate_event() - Sheet {sheet_name}")
        else:
            log.debug(f"calculate.set_doc_sheets_calculate_event() Sheet {sheet_name} does not have OnCalculate event")


def remove_doc_sheets_calculate_event(doc: CalcDoc):
    """
    Removes the Script event from the OnCalculate event of the sheets.

    This removes the OnCalculate events for all sheet without checking for existing.

    If the document has no Python code added by this extension, then it makes sense to remove the event.
    If the event is not removed then the document will prompt for permission to run the script even if there are no other scripts attached to the document.
    """
    cfg = Config()
    log = LogInst()  # singleton
    log.debug("calculate.remove_doc_sheets_calculate_event()")
    new_script = _get_new_script()
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
                        uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", ())  # type: ignore
                        uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))  # type: ignore
                        continue
            except mEx.PropertyError:
                log.debug(
                    f"calculate.remove_doc_sheets_calculate_event() - Sheet {sheet_name} - PropertyError Script not found"
                )
        else:
            log.debug(
                f"calculate.remove_doc_sheets_calculate_event() Sheet {sheet_name} does not have OnCalculate event"
            )
