from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code import QryCellSrcCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_SRC_CODE, CELL_SRC_CODE_EXIST
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code_exist import (
        QryCellSrcCodeExist,
    )
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code import QryCellSrcCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.const.cache_const import CELL_SRC_CODE, CELL_SRC_CODE_EXIST
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code_exist import QryCellSrcCodeExist


class CmdCellSrcCode(CmdBase, LogMixin, CmdCellCacheT):
    """Add OnCalculate event to sheet"""

    def __init__(self, uri: str, cell: CalcCell, code: str, src_provider: PySrcProvider | None = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL_CACHE
        self._uri = uri
        self._cell = cell
        self._code = code
        self._src_provider = src_provider
        self._current_src = cast(str | None, NULL_OBJ)
        self._current_exist = cast(bool, NULL_OBJ)

    def _get_current_src_code(self) -> str | None:
        qry = QryCellSrcCode(uri=self._uri, cell=self.cell, src_provider=self._src_provider)
        return self._execute_qry(qry)

    def _get_src_code_exist(self) -> bool:
        qry = QryCellSrcCodeExist(uri=self._uri, cell=self.cell, src_provider=self._src_provider)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        if self._current_src is NULL_OBJ:
            self._current_src = self._get_current_src_code()

        if self._current_exist is NULL_OBJ:
            self._current_exist = self._get_src_code_exist()

        self.success = False
        try:
            py_code = PySource(uri=self._uri, cell=self.cell.cell_obj, src_provider=self._src_provider)
            py_code.source_code = self._code
        except Exception:
            self.log.exception("Error setting cell Code")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

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

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (CELL_SRC_CODE, CELL_SRC_CODE_EXIST)
