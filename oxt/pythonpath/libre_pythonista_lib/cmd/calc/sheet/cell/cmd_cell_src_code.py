from __future__ import annotations
from typing import Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_SRC_CODE, CELL_SRC_CODE_EXIST
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code_exist import QryCellSrcCodeExist
else:
    from libre_pythonista_lib.pyc.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code import QryCellSrcCode
    from libre_pythonista_lib.query.qry_handler_no_cache import QryHandlerNoCache
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.const.cache_const import CELL_SRC_CODE, CELL_SRC_CODE_EXIST
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_src_code_exist import QryCellSrcCodeExist


class CmdCellSrcCode(LogMixin, CmdCellCacheT):
    """Add OnCalculate event to sheet"""

    def __init__(self, uri: str, cell: CalcCell, code: str, src_provider: PySrcProvider | None = None) -> None:
        LogMixin.__init__(self)
        self._success = False
        self._uri = uri
        self._cell = cell
        self._code = code
        self._kind = CalcCmdKind.CELL_CACHE
        self._src_provider = src_provider
        self._current_src = self._get_current_src_code()
        self._current_exist = self._get_src_code_exist()

    def _get_current_src_code(self) -> str | None:
        qry = QryCellSrcCode(uri=self._uri, cell=self.cell, src_provider=self._src_provider)
        handler = QryHandlerNoCache()

        return handler.handle(qry)

    def _get_src_code_exist(self) -> bool:
        qry = QryCellSrcCodeExist(uri=self._uri, cell=self.cell, src_provider=self._src_provider)
        handler = QryHandlerNoCache()
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
            if self._current_exist:
                if self._current_src is None:
                    self.log.error("Failed to undo. Current source code is None.")
                    return
                py_code.source_code = self._current_src
            else:
                py_code.del_source()

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
        return (CELL_SRC_CODE, CELL_SRC_CODE_EXIST)

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.CELL_CACHE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
