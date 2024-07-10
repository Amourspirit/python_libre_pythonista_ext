"""
Manages the sheet events.
Updates caches when cell are modified, added, removed.
Manages adding and removing listeners to cells.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from . import calculate as SheetCalculate
from ..const.event_const import SHEET_ACTIVATION, DOCUMENT_SAVING
from ..utils.singleton_base import SingletonBase
from ..event.shared_event import SharedEvent
from ..code.py_source_mgr import PyInstance

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


# sheet.listen.sheet_activation_listener.SheetActivationListener triggers the event


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
        self._fn_on_calc_sheet_activated = self._on_calc_sheet_activated
        self._fn_on_calc_sheet_saving = self._on_calc_sheet_saving
        self._ensure_sheet_calculate_event()
        self._se.subscribe_event(SHEET_ACTIVATION, self._fn_on_calc_sheet_activated)
        self._se.subscribe_event(DOCUMENT_SAVING, self._fn_on_calc_sheet_saving)
        self._is_init = True

    def _on_calc_sheet_activated(self, src: Any, event: EventArgs) -> None:
        try:
            self._calc_event_ensured = False
            self._sheet = self._doc.sheets.get_sheet(sheet=event.event_data.sheet)
            with self._log.noindent():
                if self._log.is_debug:
                    self._log.debug(f"Sheet activated {self._sheet.name}")

            self._ensure_sheet_calculate_event()
        except Exception:
            with self._log.noindent():
                self._log.exception("Error activating sheet")

    def _on_calc_sheet_saving(self, src: Any, event: EventArgs) -> None:
        try:
            with self._log.noindent():
                if self._log.is_debug:
                    self._log.debug(f"Sheet Saving Event for {self._sheet.name}")
            # when the sheet is saved, Events may get removed.
            try:
                SheetCalculate.remove_doc_sheets_calculate_event(self._doc)
            except Exception:
                self._log.exception("Error removing sheet calculate event")
            self._calc_event_ensured = False
        except Exception:
            with self._log.noindent():
                self._log.exception("Error cleaning up sheet")

    def _ensure_sheet_calculate_event(self):
        """Make sure the sheet has the calculate event."""
        try:
            if self._calc_event_ensured:
                self._log.debug("Sheet calculate event already ensured")
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
