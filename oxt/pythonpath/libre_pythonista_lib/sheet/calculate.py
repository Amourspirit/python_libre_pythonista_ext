from __future__ import unicode_literals, annotations
from typing import cast, TYPE_CHECKING, Tuple
import uno
from ooodev.utils.props import Props
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.exceptions import ex as mEx  # noqa: N812
from ..log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.container import XNameReplace
    from com.sun.star.beans import PropertyValue
    from ....___lo_pip___.basic_config import BasicConfig as Config
else:
    from ___lo_pip___.basic_config import BasicConfig as Config


def get_script_url() -> str:
    cfg = Config()
    location = "share:uno_packages" if cfg.is_shared_installed else "user:uno_packages"
    return f"vnd.sun.star.script:{cfg.oxt_name}.oxt|python|scripts|{cfg.py_script_sheet_on_calculate}${cfg.macro_sheet_on_calculate}?language=Python&location={location}"


def get_sheet_calculate_event(sheet: CalcSheet) -> str:
    """
    Gets the sheet current Script value.
    """
    events = cast("XNameReplace", sheet.component.getEvents())  # type: ignore
    if events.hasByName("OnCalculate"):
        try:
            current_props = cast("Tuple[PropertyValue, ...]", events.getByName("OnCalculate"))
            if current_props:
                return Props.get_value("Script", current_props)  # type: ignore
        except Exception:
            log = LogInst()
            log.exception("calculate.sheet_has_calculate_event() - Sheet %s", sheet.name)

    return ""


def sheet_has_calculate_event(sheet: CalcSheet) -> bool:
    """
    Check if the sheet has the specified event.
    """
    value = get_sheet_calculate_event(sheet)
    if not value:
        return False
    new_script = get_script_url()
    return value == new_script


def set_sheet_calculate_event(sheet: CalcSheet, script: str = "") -> bool:
    """
    Sets the OnCalculate event for a given CalcSheet.
    This function sets or replaces the OnCalculate event for the provided CalcSheet.
    If a script is provided, it will be used for the event; otherwise, a new script
    will be generated and used.

    Args:
        sheet (CalcSheet): The CalcSheet object for which the OnCalculate event is to be set.
        script (str, optional): The script to be used for the OnCalculate event. Defaults to an empty string.

    Returns:
        bool: True if the event was set successfully; otherwise, False.

    Raises:
        Exception: If there is an error while setting the OnCalculate event.

    Logs:
        Logs debug information about the process and any exceptions that occur.
    """
    result = False
    log = LogInst()  # singleton
    log.debug("calculate.set_sheet_calculate_event()")
    events = cast("XNameReplace", sheet.component.getEvents())  # type: ignore
    if events.hasByName("OnCalculate"):
        try:
            new_script = script if script else get_script_url()
            try:
                dict_props = {}
                dict_props["Script"] = new_script
                dict_props["EventType"] = "Script"
                data = Props.make_props(**dict_props)
                uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", data)  # type: ignore
                uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))  # type: ignore
                log.debug("calculate.set_sheet_calculate_event() Sheet %s - OnCalculate event replaced", sheet.name)
                result = True
            except Exception:
                log.exception("set_doc_sheets_calculate_event() - Sheet %s", sheet.name)

        except Exception:
            log.exception("calculate.set_sheet_calculate_event() - Sheet %s", sheet.name)
    else:
        log.debug("calculate.set_sheet_calculate_event() Sheet %s does not have OnCalculate event", sheet.name)
    return result


def set_doc_sheets_calculate_event(doc: CalcDoc, script: str = "") -> None:
    """
    Set the OnCalculate event for all sheets in the document.
    Unless the current event is the same as the new event it will be replaced.

    Args:
        doc (CalcDoc): CalcDoc instance
        script (str, optional): The script to be attached to the event. Defaults to "".
            If not provided a new script will be created.

    Note:
        It is possible that this sheet could be loaded into two different instances of CalcDoc with the same
        version of the extension installed. On may be installed the Shared version and the other the User version.
        In this case the events will be replaced with the correct version of the script.
    """
    log = LogInst()  # singleton
    log.debug("calculate.set_doc_sheets_calculate_event()")
    # vnd.sun.star.script:LibrePythonista.oxt|python|scripts|share_event.py$formulas_calc?language=Python&location=user:uno_packages

    new_script = script if script else get_script_url()
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
                        log.debug("Sheet %s already has correct OnCalculate event", sheet_name)
                        continue
            except mEx.PropertyError:
                log.debug(
                    "calculate.set_doc_sheets_calculate_event() - Sheet %s - PropertyError Script not found",
                    sheet_name,
                )

            try:
                dict_props = {}
                dict_props["Script"] = new_script
                dict_props["EventType"] = "Script"
                data = Props.make_props(**dict_props)
                uno_data = uno.Any("[]com.sun.star.beans.PropertyValue", data)  # type: ignore
                uno.invoke(events, "replaceByName", ("OnCalculate", uno_data))  # type: ignore
                log.debug(
                    "calculate.set_doc_sheets_calculate_event() Sheet %s - OnCalculate event replaced", sheet_name
                )
            except Exception:
                log.exception("calculate.set_doc_sheets_calculate_event() - Sheet %s", sheet_name)
        else:
            log.debug(
                "calculate.set_doc_sheets_calculate_event() Sheet %s does not have OnCalculate event", sheet_name
            )


def remove_doc_sheet_calculate_event(sheet: CalcSheet) -> None:
    """
    Removes the Script event from the OnCalculate event of the sheets.

    This removes the OnCalculate events for all sheet without checking for existing.

    If the document has no Python code added by this extension, then it makes sense to remove the event.
    If the event is not removed then the document will prompt for permission to run the script even if there are no other scripts attached to the document.
    """
    log = LogInst()  # singleton
    log.debug("calculate.remove_doc_sheets_calculate_event()")
    new_script = get_script_url()
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
        except mEx.PropertyError:
            log.debug(
                "calculate.remove_doc_sheets_calculate_event() - Sheet %s - PropertyError Script not found",
                sheet_name,
            )
    else:
        log.debug("calculate.remove_doc_sheets_calculate_event() Sheet %s does not have OnCalculate event", sheet_name)


def remove_doc_sheets_calculate_event(doc: CalcDoc) -> None:
    """
    Removes the Script event from the OnCalculate event of the sheets.

    This removes the OnCalculate events for all sheet without checking for existing.

    If the document has no Python code added by this extension, then it makes sense to remove the event.
    If the event is not removed then the document will prompt for permission to run the script even if there are no other scripts attached to the document.
    """
    log = LogInst()  # singleton
    log.debug("calculate.remove_doc_sheets_calculate_event()")
    new_script = get_script_url()
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
                    "calculate.remove_doc_sheets_calculate_event() - Sheet %s - PropertyError Script not found",
                    sheet_name,
                )
        else:
            log.debug(
                "calculate.remove_doc_sheets_calculate_event() Sheet %s does not have OnCalculate event", sheet_name
            )
