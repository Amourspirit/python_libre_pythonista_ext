from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING
import time

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcCell
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_SRC_CODE
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.pyc.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.const.cache_const import CELL_SRC_CODE
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

# this class should be call in:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache

# this class should be called with:
# pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_handler_cell_cache.CmdHandlerCellCache


class CmdCellSrcCode(LogMixin, CmdCellCacheT):
    """Add OnCalculate event to sheet"""

    def __init__(self, uri: str, cell: CalcCell, code: str, src_provider: PySrcProvider | None = None) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._uri = uri
        self._cell = cell
        self._code = code
        self._src_provider = src_provider
        self._current_src = self._get_current_src_code()

    def _get_current_src_code(self) -> str | None:
        qry = QryCellSrcCode(uri=self._uri, cell=self.cell, src_provider=self._src_provider)
        handler = QryHandler()

        return handler.handle(qry)

    def execute(self) -> None:
        self._success = False
        try:
            py_code = PySource(uri=self._uri, cell=self.cell.cell_obj, src_provider=self._src_provider)
            py_code.source_code = self._code
        except Exception:
            self.log.exception("Error setting cell Code")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        try:
            py_code = PySource(uri=self._uri, cell=self.cell.cell_obj, src_provider=self._src_provider)
            if self._current_src is None:
                py_code.del_source()
            else:
                py_code.source_code = self._current_src

            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code")

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (CELL_SRC_CODE,)

    @property
    def kind(self) -> CalcCmdKind:
        return CalcCmdKind.CELL_CACHE
