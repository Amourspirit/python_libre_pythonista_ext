from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

# this class should be call in:
# libre_pythonista_lib.cq.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache

# this class should be called with:
# pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_handler_cell_cache.CmdHandlerCellCache


class CmdCellExtraDel(CmdBase, LogMixin, CmdCellT):
    """Deletes an extra data of a cell"""

    def __init__(self, cell: CalcCell, name: str) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._name = name
        self._current_value = NULL_OBJ
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_current_value(self) -> Any:  # noqa: ANN401
        qry = QryCellPropValue(cell=self._cell, name=self._name)
        return self._execute_qry(qry)  # returns NULL_OBJ if not found

    @override
    def execute(self) -> None:
        if self._current_value is NULL_OBJ:
            self._current_value = self._get_current_value()

        self.success = False
        try:
            if self._cell.extra_data.has(self._name):
                del self._cell.extra_data[self._name]
        except Exception:
            self.log.exception("Error setting cell Code")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if self._current_value is NULL_OBJ:
            try:
                if self._cell.has_custom_property(self._name):
                    self._cell.remove_custom_property(self._name)
            except Exception:
                self.log.exception("Error undoing cell Code")
        else:
            try:
                self._cell.set_custom_property(self._name, self._current_value)
                self.log.debug("Successfully executed undo command.")
                return
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
