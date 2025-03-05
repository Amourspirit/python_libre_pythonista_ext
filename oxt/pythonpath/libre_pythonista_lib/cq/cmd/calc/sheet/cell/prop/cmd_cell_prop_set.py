from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdCellPropSet(CmdBase, LogMixin, CmdCellT):
    """Sets the custom property of a cell"""

    def __init__(self, cell: CalcCell, name: str, value: Any) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._name = name
        self._value = value
        self._current_value = NULL_OBJ

    def _get_current_value(self) -> Any:  # noqa: ANN401
        qry = QryCellPropValue(cell=self._cell, name=self._name)
        return self._execute_qry(qry)  # returns NULL_OBJ if not found

    @override
    def execute(self) -> None:
        if self._current_value is NULL_OBJ:
            self._current_value = self._get_current_value()

        self.success = False
        try:
            self._cell.set_custom_property(self._name, self._value)
        except Exception:
            self.log.exception("Error setting cell Code")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if self._current_value is not NULL_OBJ:
            try:
                self._cell.set_custom_property(self._name, self._current_value)
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error undoing cell Code")
        else:
            self.log.debug("Undo not needed.")

    @override
    def undo(self) -> None:
        if self.success and self._current_value is not NULL_OBJ:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
