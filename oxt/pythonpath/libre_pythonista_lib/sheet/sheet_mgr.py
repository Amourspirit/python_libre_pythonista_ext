"""
Manages the sheet events.
Updates caches when cell are modified, added, removed.
Manages adding and removing listeners to cells.
"""

from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from . import calculate as SheetCalculate
from ..const.event_const import (
    SHEET_ACTIVATION,
    DOCUMENT_SAVING,
    # LP_DISPATCHED_CMD,
    LP_DISPATCHING_CMD,
    SHEET_MODIFIED,
    PYC_FORMULA_ENTER,
)
from ..const import UNO_DISPATCH_PYC_FORMULA, UNO_DISPATCH_PYC_FORMULA_DEP
from ..utils.singleton_base import SingletonBase
from ..event.shared_event import SharedEvent
from ..code.py_source_mgr import PyInstance

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


# sheet.listen.sheet_activation_listener.SheetActivationListener triggers the event

# The SheetMgr class is responsible for managing the sheet events.
# Specifically it must ensure that the LibrePythonista controls have a listener present to activate the menus on click.
# Currently there seems to be no solution for this other then attaching a macro to the sheets Formula Calculated event.
# Most Likely the SheetModified event can inform SheetMgr when to attach the macro to the sheet if it is not already present.
# For more robustness will also check when the sheet is activated and when appropriate LP_DISPATCHED_CMD dispatch is made.


class SheetMgr(SingletonBase):
    """
    Manages the sheet events for the active sheet.

    Activate sheet is automatically set when the sheet is activated.
    """

    def __init__(self, doc: CalcDoc):
        if getattr(self, "_is_init", False):
            return
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.noindent():
            self._log.debug(f"Initializing {self.__class__.__name__}")
        self._doc = doc
        self._se = SharedEvent(doc)
        self._sheet = doc.get_active_sheet()
        self._calc_event_ensured = False
        self._calc_event_chk_code = True
        self._ensuring_sheet_calculate_event = False
        self._fn_on_calc_sheet_activated = self._on_calc_sheet_activated
        self._fn_on_calc_sheet_saving = self._on_calc_sheet_saving
        self._fn_on_dispatching_cmd = self._on_dispatching_cmd
        self._fn_on_calc_sheet_modified = self._on_calc_sheet_modified
        self._fn_on_calc_pyc_formula_enter = self._on_calc_pyc_formula_enter
        # self._ensure_sheet_calculate_event()
        self._se.subscribe_event(SHEET_ACTIVATION, self._fn_on_calc_sheet_activated)
        self._se.subscribe_event(SHEET_MODIFIED, self._fn_on_calc_sheet_modified)
        self._se.subscribe_event(LP_DISPATCHING_CMD, self._fn_on_dispatching_cmd)
        self._se.subscribe_event(DOCUMENT_SAVING, self._fn_on_calc_sheet_saving)
        self._se.subscribe_event(PYC_FORMULA_ENTER, self._fn_on_calc_pyc_formula_enter)
        self._is_init = True

    # region Event Handlers

    def _on_calc_pyc_formula_enter(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_pyc_formula_enter()")
        try:
            self._calc_event_ensured = False
            self._calc_event_chk_code = False
            self._sheet = cast(CalcSheet, event.event_data.sheet)
            with self._log.noindent():
                if self._log.is_debug:
                    self._log.debug(f"Formula entered {self._sheet.name}")

            self._ensure_sheet_calculate_event()
        except Exception:
            with self._log.noindent():
                self._log.exception("_on_calc_pyc_formula_enter() Error")

    def _on_calc_sheet_activated(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_sheet_activated()")
        try:
            self._calc_event_ensured = False
            self._calc_event_chk_code = True
            self._sheet = self._doc.sheets.get_sheet(sheet=event.event_data.sheet)
            with self._log.noindent():
                if self._log.is_debug:
                    self._log.debug(f"Sheet activated {self._sheet.name}")

            self._ensure_sheet_calculate_event()
        except Exception:
            with self._log.noindent():
                self._log.exception("Error activating sheet")

    def _on_calc_sheet_modified(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_sheet_modified()")
        try:
            self._calc_event_ensured = False
            self._calc_event_chk_code = True
            with self._log.noindent():
                if self._log.is_debug:
                    sheet = None
                    try:
                        evo = event.event_data.event
                        sheet = CalcSheet.from_obj(evo.Source)
                    except Exception as err:
                        self._log.debug(f"{err}")
                        sheet = None
                    if sheet:
                        self._log.debug(f"Sheet Modified  {sheet.name}")
                    else:
                        self._log.debug("Sheet Modified. Sheet not found")

            self._ensure_sheet_calculate_event()
        except Exception:
            with self._log.noindent():
                self._log.exception("_on_calc_sheet_modified() Error")

    def _on_dispatching_cmd(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_dispatching_cmd()")
        try:
            self._calc_event_ensured = False
            self._calc_event_chk_code = False
            ed = cast(DotDict, event.event_data)
            cmd = cast(str, ed.cmd)
            if cmd in (UNO_DISPATCH_PYC_FORMULA, UNO_DISPATCH_PYC_FORMULA_DEP):
                self._calc_event_ensured = False
                with self._log.noindent():
                    if self._log.is_debug:
                        self._log.debug(f"Dispatch Command {cmd}")
                self._ensure_sheet_calculate_event()

        except Exception:
            with self._log.noindent():
                self._log.exception("Error activating sheet")

    def _on_calc_sheet_saving(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_sheet_saving()")
        try:
            with self._log.noindent():
                if self._log.is_debug:
                    self._log.debug(f"Sheet Saving Event for {self._sheet.name}")
            # when the sheet is saved, Events may get removed.
            try:
                self.clean_up_sheet_calculate_event()
            except Exception:
                self._log.exception("Error removing sheet calculate event")
            self._calc_event_ensured = False
        except Exception:
            with self._log.noindent():
                self._log.exception("Error cleaning up sheet")

    # endregion Event Handlers

    def _ensure_sheet_calculate_event(self):
        """Make sure the sheet has the calculate event."""
        self._log.debug("_ensure_sheet_calculate_event()")
        if self._ensuring_sheet_calculate_event:
            self._log.debug("Already ensuring sheet calculate event")
            return

        self._ensuring_sheet_calculate_event = True

        try:
            if self._calc_event_ensured:
                self._log.debug("Sheet calculate event already ensured")
                return
            if self._calc_event_chk_code:
                py_src = PyInstance(self._doc)  # singleton
                if not py_src.has_code():
                    self._log.debug("No Code Found for document")
                    return
            if not SheetCalculate.sheet_has_calculate_event(self._sheet):
                if self._log.is_debug:
                    self._log.debug(f"Sheet {self._sheet.name} does not have calculate event")
                SheetCalculate.set_sheet_calculate_event(self._sheet)
                if self._log.is_debug:
                    self._log.debug(f"Sheet {self._sheet.name} calculate event set")

            self._calc_event_ensured = True
        except Exception:
            with self._log.noindent():
                self._log.exception("Error ensuring sheet calculate event")
        finally:
            self._ensuring_sheet_calculate_event = False

    def ensure_sheet_calculate_event(self):
        """Make sure the sheet has the calculate event."""
        with self._log.indent(True):
            self._ensure_sheet_calculate_event()

    def clean_up_sheet_calculate_event(self):
        """Remove the sheet calculate event if there is not Python code in the document."""
        py_src = PyInstance(self._doc)  # singleton
        if not py_src.has_code():
            self._log.debug("No Code Found for document")
            SheetCalculate.remove_doc_sheets_calculate_event(self._doc)
        else:
            self._log.debug("Code Found for document")

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
