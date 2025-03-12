from __future__ import annotations
from typing import Any, List, TYPE_CHECKING

from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import QryCellPropValues
else:
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import QryCellPropValues

# tested in: tests/test_cmd_qry/test_cell/prop/test_cell_props_set.py


class CmdCellPropsSet(CmdBase, LogMixin, CmdCellT):
    """
    Command to set custom properties on a Calc cell with undo capability.

    This command implements the Command pattern to set custom properties on a cell
    while maintaining the ability to undo the changes if needed.

    Args:
        cell (CalcCell): The target cell to set properties on
        **props (Any): Keyword arguments representing the properties to set
    """

    def __init__(self, cell: CalcCell, **props: Any) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._props = props
        self._current_values = None
        self._success_props: List[str] = []

    def _get_current_values(self) -> DotDict[Any]:
        """
        Gets the current values of properties that will be modified.

        Returns:
            DotDict[Any]: Dictionary containing current property values
        """
        qry = QryCellPropValues(cell=self._cell, prop_names=self._props.keys())
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command by setting the specified properties on the cell.

        If any error occurs during execution, the command will attempt to undo
        any changes that were successfully made.
        """
        self._success_props.clear()
        if not isinstance(self._current_values, DotDict):
            self._current_values = self._get_current_values()

        self.success = False
        try:
            for name, value in self._props.items():
                self._cell.set_custom_property(name, value)
                self._success_props.append(name)
        except Exception:
            self.log.exception("Error setting custom properties")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to restore the cell's properties to their previous state.
        """
        if not isinstance(self._current_values, DotDict):
            self.log.debug("No Current State. Unable to undo.")
            return
        if not self._success_props:
            self.log.debug("No properties set. Unable to undo.")
            return

        try:
            for name in self._success_props:
                current_value = self._current_values.get(name, NULL)
                if current_value is NULL:
                    if self._cell.has_custom_property(name):
                        self._cell.remove_custom_property(name)
                else:
                    self._cell.set_custom_property(name, current_value)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code")

    @override
    def undo(self) -> None:
        """
        Public method to undo the command if it was successfully executed.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell associated with this command.

        Returns:
            CalcCell: The target cell
        """
        return self._cell
