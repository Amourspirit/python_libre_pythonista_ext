from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
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
        self.log.debug("init done for cell %s  for name %s", cell.cell_obj, name)

    def _get_current_value(self) -> Any:  # noqa: ANN401
        qry = QryCellPropValue(cell=self._cell, name=self._name, default=NULL)
        return self._execute_qry(qry)  # returns NULL_OBJ if not found

    @override
    def execute(self) -> None:
        if self._current_value is NULL_OBJ:
            self._current_value = self._get_current_value()

        self.success = False
        try:
            self._cell.set_custom_property(self._name, self._value)
        except Exception:
            self.log.exception("Error setting custom property %s", self._name)
            return
        self.log.debug("Successfully executed command for %s with %s", self.cell.cell_obj, self._name)
        self.success = True

    def _undo(self) -> None:
        if self._current_value is not NULL_OBJ:
            try:
                if self._current_value is NULL:
                    if self._cell.has_custom_property(self._name):
                        self._cell.remove_custom_property(self._name)
                else:
                    self._cell.set_custom_property(self._name, self._current_value)
                self.log.debug("Successfully executed undo command for %s with %s", self.cell.cell_obj, self._name)
            except Exception:
                self.log.exception("Error executing undo for cell: %s", self._cell.cell_obj)
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
