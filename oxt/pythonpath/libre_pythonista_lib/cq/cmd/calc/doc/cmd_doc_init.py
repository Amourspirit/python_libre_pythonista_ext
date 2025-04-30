from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_INIT_COMPLETED
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.const.cache_const import DOC_INIT_COMPLETED
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.utils.result import Result

# see: libre_pythonista_lib.cq.qry.calc.doc.qry_doc_init.QryDocInit


class CmdDocInit(CmdBase, LogMixin, CmdDocT):
    """Sets a flag that the document has been initialized."""

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)

        # doc is not needed, Just here to satisfy the CmdDocT interface
        # see: libre_pythonista_lib.cq.cmd.calc.init_commands.cmd_init_doc.CmdInitDoc
        self._doc = doc
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _get_globals(self) -> DocGlobals | None:
        qry = QryDocGlobals(self._doc.runtime_uid)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        return None

    @override
    def execute(self) -> None:
        self.success = False
        doc_globals = self._get_globals()

        if doc_globals is None:
            self.log.error("DocGlobals is None. Unable to execute command.")
            return
        doc_globals.mem_cache[DOC_INIT_COMPLETED] = "1"
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        self.log.debug("Undo not needed for this command.")
