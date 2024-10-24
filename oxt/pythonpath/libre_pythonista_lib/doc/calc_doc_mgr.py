"""
Manages the document events.
Manages adding and removing listeners to document and sheets.
"""

from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

import time

from ooodev.calc import CalcDoc, CalcSheet
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.exceptions import ex as mEx

from ..const.event_const import (
    SHEET_ACTIVATION,
    LP_DISPATCHING_CMD,
    LP_DISPATCHED_CMD,
    SHEET_MODIFIED,
    PYC_FORMULA_ENTER,
    OXT_INIT,
    LP_DOC_EVENTS_ENSURED,
)
from ..const import UNO_DISPATCH_PYC_FORMULA, UNO_DISPATCH_PYC_FORMULA_DEP
from ..utils.singleton_base import SingletonBase
from ..event.shared_event import SharedEvent
from ..state.calc_state_mgr import CalcStateMgr
from ..dispatch import dispatch_mgr  # type: ignore


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class CalcDocMgr(SingletonBase):
    """
    Manages the sheet events for the active sheet.

    Activate sheet is automatically set when the sheet is activated.
    """

    def __init__(self):
        if getattr(self, "_is_init", False):
            return
        self.runtime_uid: str
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.noindent():
            self._log.debug(f"Initializing {self.__class__.__name__}")
        self._doc = cast(CalcDoc, self.singleton_doc)

        self._state_mgr = CalcStateMgr(self._doc)
        self._init_cell_mgr = False
        self._init_doc_listeners_sheet = False
        self._init_doc_view_listeners = False
        self._calc_event_ensured = False
        self._calc_event_chk_code = True
        self._is_init_events = False
        self._events_ensured = False
        self._events_ensuring = False
        self._register_dispatch_mgr()
        if not self._state_mgr.is_imports2_ready:
            # if not ready then a restart of LibreOffice is required.
            self._log.debug("Imports2 is not ready. Returning.")
            return
        self._se = SharedEvent(self._doc)
        self._init_events()
        # if self._state_mgr.is_pythonista_doc:
        #     self._log.debug("__init__() Document is a LibrePythonista")
        #     self.ensure_events()
        self._is_init = True

    # region Events

    # region init events

    def _init_events(self) -> None:
        self._fn_on_calc_sheet_activated = self._on_calc_sheet_activated
        self._fn_on_dispatching_cmd = self._on_dispatching_cmd
        self._fn_on_dispatched_cmd = self._on_dispatched_cmd
        self._fn_on_calc_sheet_modified = self._on_calc_sheet_modified
        self._fn_on_calc_pyc_formula_enter = self._on_calc_pyc_formula_enter
        # self._ensure_events()
        self._se.subscribe_event(SHEET_ACTIVATION, self._fn_on_calc_sheet_activated)
        self._se.subscribe_event(SHEET_MODIFIED, self._fn_on_calc_sheet_modified)
        self._se.subscribe_event(LP_DISPATCHING_CMD, self._fn_on_dispatching_cmd)
        self._se.subscribe_event(LP_DISPATCHED_CMD, self._fn_on_dispatched_cmd)
        self._se.subscribe_event(PYC_FORMULA_ENTER, self._fn_on_calc_pyc_formula_enter)

    # endregion init events

    # region Event Handlers

    def _on_calc_pyc_formula_enter(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_pyc_formula_enter()")
        try:
            self._state_mgr.is_pythonista_doc = True
            self._calc_event_ensured = False
            self._calc_event_chk_code = False
            self._sheet = cast(CalcSheet, event.event_data.sheet)
            with self._log.noindent():
                if self._log.is_debug:
                    self._log.debug(f"Formula entered {self._sheet.name}")

            self.ensure_events()
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

            self.ensure_events()
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

            self.ensure_events()
        except Exception:
            with self._log.noindent():
                self._log.exception("_on_calc_sheet_modified() Error")

    def _on_dispatching_cmd(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_dispatched_cmd()")
        try:
            self._state_mgr.is_pythonista_doc = True
            self._calc_event_ensured = False
            self._calc_event_chk_code = False
            ed = cast(DotDict, event.event_data)
            cmd = cast(str, ed.cmd)
            if cmd in (UNO_DISPATCH_PYC_FORMULA, UNO_DISPATCH_PYC_FORMULA_DEP):
                self._calc_event_ensured = False
                with self._log.noindent():
                    if self._log.is_debug:
                        self._log.debug(f"Dispatch Command {cmd}")
                self.ensure_events()

        except Exception:
            with self._log.noindent():
                self._log.exception("Error activating sheet")

    def _on_dispatched_cmd(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_dispatched_cmd()")
        pass

    # endregion Event Handlers

    # endregion Events

    def _initialize_document_listeners(self) -> bool:
        # if not self._state_mgr.is_pythonista_doc:
        #     self._log.debug("_initialize_document_listeners() Document not currently a LibrePythonista. Returning.")
        #     return False

        from ..doc.listen.document_event_listener import DocumentEventListener
        from ..cell.cell_update_mgr import CellUpdateMgr

        result = False

        try:
            # check to see if the extension location is the same for this instance
            # as the previous time this document was opened.
            # The document may be opened in a different environment,
            # The extension location may be in shared instead of users or vice versa.
            cell_update = CellUpdateMgr(self._doc)
            cell_update.update_cells()
        except Exception:
            self._log.error("Error updating cells with CellUpdateMgr", exc_info=True)
            return result
        try:
            self._doc.component.addDocumentEventListener(DocumentEventListener())
            self._log.debug("Document event listener added")
            result = True
        except Exception:
            self._log.error("Error adding document event listener", exc_info=True)
        return result

    def _initialize_sheet_listeners(self) -> bool:
        # if not self._state_mgr.is_pythonista_doc:
        #     self._log.debug("_initialize_document_listeners() Document not currently a LibrePythonista. Returning.")
        #     return False

        # only run if state_mgr.is_imports2_ready
        self._log.debug("_initialize_sheet_listeners()")
        try:
            from ..sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
            from ..sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
            from ..sheet.listen.sheet_activation_listener import SheetActivationListener
        except ImportError:
            self._log.exception("Sheet listeners not imported. Returning.")
            return False

        view = None
        try:
            view = self._doc.get_view()
        except mEx.MissingInterfaceError as e:
            self._log.debug(f"Error getting view from document. {e}")
            view = None

        if view is None:
            self._log.debug("View is None. May be print preview. Returning.")
            return False
        try:
            if view.view_controller_name == "Default":
                self._log.debug("View controller is Default.")
            else:
                # this could mean that the print preview has been activated.
                # Print Preview view controller Name: PrintPreview
                self._log.debug(f"'{view.view_controller_name}' is not the default view controller. Returning.")
                return False

            if not self._state_mgr.is_imports2_ready:
                # if not ready then a restart of LibreOffice is required.
                self._log.debug("Imports2 is not ready. Returning.")
                return False

            for sheet in self._doc.sheets:
                unique_id = sheet.unique_id
                if not CodeSheetModifyListener.has_listener(unique_id):
                    listener = CodeSheetModifyListener(unique_id)  # singleton
                    sheet.component.addModifyListener(listener)
                else:
                    listener = CodeSheetModifyListener.get_listener(unique_id)  # singleton
                    sheet.component.removeModifyListener(listener)
                    sheet.component.addModifyListener(listener)
        except Exception:
            self._log.exception("Error initializing sheet listeners")
            return False

        # adds new modifier listeners to new sheets
        try:
            code_sheet_activation_listener = CodeSheetActivationListener()
            sheet_act_listener = SheetActivationListener()
            view.component.removeActivationEventListener(code_sheet_activation_listener)
            view.component.addActivationEventListener(code_sheet_activation_listener)
            view.component.removeActivationEventListener(sheet_act_listener)
            view.component.addActivationEventListener(sheet_act_listener)

            if view.is_form_design_mode():
                try:
                    self._log.debug("Setting form design mode to False")
                    view.set_form_design_mode(False)
                    self._log.debug("Form design mode set to False")
                    # doc.toggle_design_mode()
                except Exception:
                    self._log.warning("Unable to set form design mode", exc_info=True)
            else:
                self._log.debug("Form design mode is False. Toggling on and off.")
                view.set_form_design_mode(True)
                time.sleep(0.1)
                view.set_form_design_mode(False)
        except Exception:
            self._log.exception("Error initializing sheet listeners")
            return False
        return True

    def _init_cell_manager(self) -> bool:
        # if not self._state_mgr.is_pythonista_doc:
        #     self._log.debug("_init_cell_manager() Document not currently a LibrePythonista. Returning.")
        #     return False

        try:
            from ..sheet.sheet_mgr import SheetMgr
            from ..cell.cell_mgr import CellMgr  # type: ignore

            _ = SheetMgr(self._doc)  # init the singleton

            cm = CellMgr(self._doc)
            cm.reset_py_inst()
            cm.add_all_listeners()

            self._doc.component.calculateAll()
            eargs = EventArgs(object())
            eargs.event_data = DotDict(
                run_id=self.runtime_uid, doc=self._doc, event=OXT_INIT, doc_type=self._doc.DOC_TYPE
            )
            self._se.trigger_event(OXT_INIT, eargs)
        except Exception:
            self._log.exception("Error initializing cell manager")
            return False
        return True

    def _register_dispatch_mgr(self) -> None:
        # Can still register the dispatch manager even if the imports are not ready.
        self._log.debug(f"Pre Dispatch manager loaded, UID: {self._doc.runtime_uid}")
        dispatch_mgr.unregister_interceptor(self._doc)
        dispatch_mgr.register_interceptor(self._doc)

    def ensure_events(self) -> None:
        """
        Make sure the sheet events and environments are set for LibrePythonista.

        Generally this method will not take any action until after the View Job has finished.

        Also the current Calc Document must be a LibrePythonista document before this method takes any action.
        """
        self._log.debug("_ensure_events()")
        if self._events_ensured:
            self._log.debug("_ensure_events() Events already ensuring. Returning.")
            return

        if not self.calc_state_mgr.is_oxt_init:
            self._log.debug("_ensure_events() Oxt not initialized. Returning.")
            return

        self._events_ensuring = True

        def ensure_sheet_mgr():
            try:
                from ..sheet.sheet_mgr import SheetMgr  # noqa # type: ignore
            except ImportError:
                self._log.error("SheetMgr not imported. Returning.")
                return
            try:
                _ = SheetMgr(doc=self._doc)  # noqa
            except Exception:
                self._log.exception("Error ensuring SheetMgr")

        try:
            if self.events_ensured:
                self._log.debug("Events already ensured. Returning.")
                self._se.trigger_event(LP_DOC_EVENTS_ENSURED, EventArgs(self))
                return

            if self._state_mgr.is_pythonista_doc:
                self._log.debug("Document is a LibrePythonista")
            else:
                self._log.debug("Document not currently a LibrePythonista. Returning.")
                return

            if self._init_doc_view_listeners:
                self._log.debug("Document view listeners already initialized.")
            else:
                self._log.debug("Document view listeners not initialized. Initializing.")
                self._init_doc_view_listeners = self._initialize_document_listeners()

            if not self._init_doc_view_listeners:
                self._log.debug("Document view listeners not initialized. Returning.")
                return

            ensure_sheet_mgr()

            if self._is_init_events:
                self._log.debug("Events already initialized.")
            else:
                self._log.debug("Events not initialized. Initializing.")
                self._init_events()
                self._is_init_events = True

            if self._init_doc_listeners_sheet:
                self._log.debug("Document listeners already initialized.")
            else:
                self._init_doc_listeners_sheet = self._initialize_sheet_listeners()

            if self._init_cell_mgr:
                self._log.debug("Cell manager already initialized.")
            else:
                self._init_cell_mgr = self._init_cell_manager()

            self._events_ensured = True
            eargs = EventArgs(self)
            eargs.event_data = DotDict(run_id=self.runtime_uid)
            self._se.trigger_event(LP_DOC_EVENTS_ENSURED, eargs)

        except Exception:
            with self._log.noindent():
                self._log.exception("Error ensuring events")
        finally:
            self._events_ensuring = False

    @property
    def doc(self) -> CalcDoc:
        return self._doc

    @property
    def events_ensured(self) -> bool:
        """
        Returns True if the events have been ensured.

        If the current Calc document is not a LibrePythonista document then this will return False.
        """
        return self._events_ensured

    @property
    def calc_state_mgr(self) -> CalcStateMgr:
        return self._state_mgr
