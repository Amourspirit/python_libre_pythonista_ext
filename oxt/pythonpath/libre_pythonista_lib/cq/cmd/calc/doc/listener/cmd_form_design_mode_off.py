from __future__ import annotations
from typing import TYPE_CHECKING
import time

from ooodev.exceptions import ex as mEx  # noqa: N812

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcSheetView
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT


class CmdFormDesignModeOff(CmdBase, LogMixin, CmdDocT):
    """Sets Form Design Mode to False"""

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._current_state = self._get_form_design_mode()

    def _get_form_design_mode(self) -> bool | None:
        view = self._get_view()
        if view is not None:
            return view.is_form_design_mode()
        return None

    def _get_view(self) -> CalcSheetView | None:
        try:
            view = self._doc.get_view()
            if view.view_controller_name == "Default":
                self.log.debug("View controller is Default.")
                return view
            else:
                # this could mean that the print preview has been activated.
                # Print Preview view controller Name: PrintPreview
                self.log.debug(
                    "'%s' is not the default view controller. Returning.",
                    view.view_controller_name,
                )
            return None

        except mEx.MissingInterfaceError as e:
            self.log.debug("Error getting view from document. %s", e)
            return None

    @override
    def execute(self) -> None:
        self.success = False
        view = self._get_view()
        if view is None:
            self.log.debug("View is None. May be print preview. Returning.")
            return
        try:
            if view.is_form_design_mode():
                self.log.debug("Form design mode is True. Setting to False.")
                view.set_form_design_mode(False)
            else:
                self.log.debug("Form design mode is False. Toggling on and off.")
                view.set_form_design_mode(True)
                time.sleep(0.1)
                view.set_form_design_mode(False)

        except Exception:
            self.log.exception("Error initializing sheet activation listener")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        if self.success:
            if self._current_state is None:
                self.log.debug("Current state is None. Unable to undo.")
                return
            view = self._get_view()
            try:
                if view is None:
                    self.log.debug("View is None. May be print preview. Returning.")
                    return
                view.set_form_design_mode(self._current_state)
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error setting form design mode")
        else:
            self.log.debug("Undo not needed.")
