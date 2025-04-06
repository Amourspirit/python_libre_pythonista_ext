from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CMD_INIT_SHEETS_KEY
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.const.cache_const import CMD_INIT_SHEETS_KEY
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result

    DocGlobals = Any

# See also: cq.cmd.calc.init_commands.cmd_init_sheets.CmdInitSheets


class QrySheetsInit(QryBase, QryT[bool]):
    def __init__(self) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.SIMPLE

    def _get_globals(self) -> DocGlobals | None:
        qry = QryDocGlobals()
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        return None

    def execute(self) -> bool:
        """
        Executes the query to check if the document sheets are initialized. The document is initialized if the
        command cq.cmd.calc.init_commands.cmd_init_sheets.CmdInitSheets has been executed.

        Returns:
            bool: True if the document sheets are initialized, False otherwise.
        """
        doc_globals = self._get_globals()
        if doc_globals is None:
            return False
        if CMD_INIT_SHEETS_KEY not in doc_globals.mem_cache:
            return False
        key_val = doc_globals.mem_cache[CMD_INIT_SHEETS_KEY]
        return key_val == "1"
