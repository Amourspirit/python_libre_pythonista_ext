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


class CmdCellPropDel(CmdBase, LogMixin, CmdCellT):
    """Deletes a custom property of a cell"""

    def __init__(self, cell: CalcCell, name: str) -> None:
        """
        Initialize command to delete a cell's custom property.

        Args:
            cell: The CalcCell to modify
            name: Name of the custom property to delete
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._name = name
        self._kind = CalcCmdKind.CELL
        self._current_value = NULL_OBJ
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_current_value(self) -> Any:  # noqa: ANN401
        """
        Gets current value of the property before deletion.

        Returns:
            Current property value or NULL_OBJ if not found
        """
        qry = QryCellPropValue(cell=self._cell, name=self._name)
        return self._execute_qry(qry)  # returns NULL_OBJ if not found

    @override
    def execute(self) -> None:
        """
        Executes the command to delete the property.
        Stores current value for undo capability.
        """
        if self._current_value is NULL_OBJ:
            self._current_value = self._get_current_value()

        self.success = False
        try:
            self._cell.remove_custom_property(self._name)
        except Exception:
            self.log.exception("Error removing custom property")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to restore the property to its previous state.
        """
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
        """
        Public method to undo the command if it was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell being modified.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
