from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.menus.cell_reg_interceptor import (
        register_interceptor,
        unregister_interceptor,
    )
    from oxt.pythonpath.libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import (
        CalcSheetCellDispatchProvider,
    )

else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.menus.cell_reg_interceptor import register_interceptor, unregister_interceptor
    from libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import CalcSheetCellDispatchProvider

# Should be called with:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache


class CmdUnRegisterDispatchInterceptor(LogMixin, CmdT):
    """Unregister Dispatch Provider Interceptor from doc"""

    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        self._success = False
        self._doc = doc
        self._kind = CalcCmdKind.SIMPLE
        self._has_instance = CalcSheetCellDispatchProvider.has_instance(doc)

    def execute(self) -> None:
        self._success = False
        try:
            if self._has_instance:
                unregister_interceptor(self._doc)
                self._has_instance = CalcSheetCellDispatchProvider.has_instance(self._doc)
            else:
                self.log.debug("Dispatch Provider Interceptor was not registered.")
                self._success = True
                return

        except Exception:
            self.log.exception("Error unregistering Dispatch Provider Interceptor")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            if CalcSheetCellDispatchProvider.has_instance(self._doc):
                self.log.debug("Dispatch Provider Interceptor already registered.")
            else:
                register_interceptor(self._doc)
                self._has_instance = CalcSheetCellDispatchProvider.has_instance(self._doc)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing Dispatch Provider Interceptor")

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
