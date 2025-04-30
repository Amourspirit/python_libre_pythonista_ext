from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.utils.result import Result


class CmdPyModuleDefault(CmdBase, LogMixin, CmdDocT):
    """Sets the default Python module in the document globals."""

    CACHE_KEY = "libre_pythonista_lib.cq.cmd.calc.doc.cmd_py_module_default"

    def __init__(self, doc: CalcDoc, mod: PyModuleT) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)

        self._doc = doc
        self._mod = mod
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

        if CmdPyModuleDefault.CACHE_KEY in doc_globals.mem_cache:
            self.log.debug("Already executed command.")
            self.log.debug("Removing cache key.")
            cache_mod = doc_globals.mem_cache[CmdPyModuleDefault.CACHE_KEY]
            if cache_mod is self._mod:
                self.log.debug("Already set to this module. Nothing to do.")
                self.success = True
                return
            del doc_globals.mem_cache[CmdPyModuleDefault.CACHE_KEY]

        doc_globals.mem_cache[CmdPyModuleDefault.CACHE_KEY] = self._mod

        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        self.log.debug("Undo not needed for this command.")
