from __future__ import annotations
from typing import TYPE_CHECKING, Union

from ooodev.exceptions import ex as mEx  # noqa: N812

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcSheetView
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import (
        CodeSheetActivationListener,
    )
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.sheet.listen.code_sheet_activation_listener import CodeSheetActivationListener
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdCodeSheetActivation(CmdBase, LogMixin, CmdDocT):
    """Adds code sheet activation listener"""

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self.kind = CalcCmdKind.SIMPLE
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _get_view(self) -> Union[CalcSheetView, None]:
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
            listener = CodeSheetActivationListener()  # singleton
            listener.set_trigger_state(True)
            view.component.removeActivationEventListener(listener)
            view.component.addActivationEventListener(listener)
        except Exception:
            self.log.exception("Error initializing sheet activation listener")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        if self.success:
            view = self._get_view()
            try:
                if view is not None:
                    listener = CodeSheetActivationListener()  # singleton
                    listener.set_trigger_state(False)
                    view.component.removeActivationEventListener(listener)
                    self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing sheet activation listener")
        else:
            self.log.debug("Undo not needed.")
