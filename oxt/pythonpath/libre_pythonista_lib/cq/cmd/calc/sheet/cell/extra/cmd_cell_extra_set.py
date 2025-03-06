from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.extra.qry_cell_extra_value import (
        QryCellExtraValue,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_del import CmdCellExtraDel
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.extra.qry_cell_extra_value import QryCellExtraValue
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_del import CmdCellExtraDel

# this class should be call in:
# libre_pythonista_lib.cq.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache

# this class should be called with:
# pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_handler_cell_cache.CmdHandlerCellCache


class CmdCellExtraSet(CmdBase, LogMixin, CmdCellT):
    """Sets the value of an extra data of a cell"""

    def __init__(self, cell: CalcCell, name: str, value: Any) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._name = name
        self._value = value
        self._null = object()
        self._current_value = self._null

    def _get_current_value(self) -> Any:  # noqa: ANN401
        # can return NULL_OBJ
        qry = QryCellExtraValue(cell=self._cell, name=self._name)
        return self._execute_qry(qry)  # returns NULL_OBJ if not found

    @override
    def execute(self) -> None:
        if self._current_value is self._null:
            self._current_value = self._get_current_value()

        self.success = False
        try:
            self._cell.extra_data[self._name] = self._value
        except Exception:
            self.log.exception("Error setting cell Code")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if self._current_value is NULL_OBJ:
            cmd = CmdCellExtraDel(cell=self._cell, name=self._name)
            self._execute_cmd(cmd)
            if cmd.success:
                self.log.debug("Successfully executed undo command.")
            else:
                self.log.error("Failed to execute undo command.")
        else:
            try:
                self._cell.extra_data[self._name] = self._current_value
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
