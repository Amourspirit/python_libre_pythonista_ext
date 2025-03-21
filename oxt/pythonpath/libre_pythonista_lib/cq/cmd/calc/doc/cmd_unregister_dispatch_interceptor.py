from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.menus.cell_reg_interceptor import (
        register_interceptor,
        unregister_interceptor,
    )
    from oxt.pythonpath.libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import (
        CalcSheetCellDispatchProvider,
    )

else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.doc.calc.doc.menus.cell_reg_interceptor import (
        register_interceptor,
        unregister_interceptor,
    )
    from libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import CalcSheetCellDispatchProvider


class CmdUnRegisterDispatchInterceptor(CmdBase, LogMixin, CmdDocT):
    """Unregister Dispatch Provider Interceptor from doc"""

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._has_instance = CalcSheetCellDispatchProvider.has_instance(doc)

    @override
    def execute(self) -> None:
        self.success = False
        try:
            if self._has_instance:
                unregister_interceptor(self._doc)
                self._has_instance = CalcSheetCellDispatchProvider.has_instance(self._doc)
            else:
                self.log.debug("Dispatch Provider Interceptor was not registered.")
                self.success = True
                return

        except Exception:
            self.log.exception("Error unregistering Dispatch Provider Interceptor")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

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

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
