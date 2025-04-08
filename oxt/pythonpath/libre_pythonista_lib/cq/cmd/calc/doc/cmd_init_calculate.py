from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_INIT_CALCULATED
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.const.cache_const import DOC_INIT_CALCULATED
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.utils.result import Result

# see: libre_pythonista_lib.cq.qry.calc.doc.qry_doc_init.QryDocInit


class CmdInitCalculate(CmdBase, LogMixin, CmdT):
    """Sets a flag that the Document Calculate All has been called."""

    def __init__(self, uid: str | None = None) -> None:
        """Constructor

        Args:
            uid (str, optional): The document uid. Defaults to None.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)

        self._uid = uid
        self._is_init = None
        if self._uid is None:
            self.log.debug("init done for doc")
        else:
            self.log.debug("init done for uid %s", self._uid)

    def _get_globals(self) -> DocGlobals | None:
        qry = QryDocGlobals(uid=self._uid)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        return None

    @override
    def execute(self) -> None:
        """Executes the command."""
        self.success = False
        doc_globals = self._get_globals()

        if doc_globals is None:
            self.log.error("DocGlobals is None. Unable to execute command.")
            return
        if DOC_INIT_CALCULATED in doc_globals.mem_cache and doc_globals.mem_cache[DOC_INIT_CALCULATED] == "1":
            self.log.debug("Already executed command.")
            self.success = True
            return
        else:
            self._is_init = False
        doc_globals.mem_cache[DOC_INIT_CALCULATED] = "1"
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        """Undoes the command."""
        if not self.success:
            self.log.debug("Undo not needed for this command.")
            return
        if self._is_init is None:
            self.log.debug("Undo not needed for this command.")
            return
        doc_globals = self._get_globals()
        if doc_globals is None:
            self.log.error("DocGlobals is None. Unable to execute command.")
            return
        if self._is_init is True:
            doc_globals.mem_cache[DOC_INIT_CALCULATED] = "1"
        else:
            del doc_globals.mem_cache[DOC_INIT_CALCULATED]
        self._is_init = None
        self.log.debug("Successfully executed undo command.")
