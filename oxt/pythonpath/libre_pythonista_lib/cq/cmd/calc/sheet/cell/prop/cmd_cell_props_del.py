from __future__ import annotations
from typing import Any, Iterable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from ooodev.utils.helper.dot_dict import DotDict
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import QryCellPropValues
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import QryCellPropValues
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class CmdCellPropsDel(CmdBase, LogMixin, CmdCellT):
    """
    Command that deletes custom properties from a LibreOffice Calc cell.

    This class implements the Command pattern for deleting custom properties from a cell,
    with support for undo operations.

    Args:
        cell (CalcCell): The target cell whose properties will be deleted.
        prop_names (Iterable[str]): Names of the properties to delete.

    Attributes:
        kind (CalcCmdKind): Identifies this as a cell-related command.
        success (bool): Indicates if the command executed successfully.
    """

    def __init__(
        self,
        cell: CalcCell,
        prop_names: Iterable[str],
    ) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._prop_names = prop_names
        self._kind = CalcCmdKind.CELL
        self._current_value = None
        self._null = object()
        self._removed: List[str] = []

    def _get_current_dot_dict(self) -> DotDict[Any]:
        """
        Gets the current property values before deletion.

        Returns:
            DotDict[Any]: Dictionary containing current property values.
        """
        qry = QryCellPropValues(cell=self._cell, prop_names=self._prop_names, default=self._null)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command by removing the specified custom properties.

        Tracks removed properties for potential undo operations.
        Sets success to True if all operations complete without error.
        """
        self._removed.clear()
        if not isinstance(self._current_value, DotDict):
            self._current_value = self._get_current_dot_dict()

        self.success = False
        try:
            for name in self._prop_names:
                if self._cell.has_custom_property(name):
                    self._cell.remove_custom_property(name)
                    self._removed.append(name)
                    self.log.debug("Successfully removed custom property: %s", name)
                else:
                    self.log.debug("Custom property not found: %s", name)
        except Exception:
            self.log.exception("Error removing custom properties")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to restore previously deleted properties.

        Restores properties using values cached before deletion.
        Clears the list of removed properties after restoration.
        """
        if not isinstance(self._current_value, DotDict):
            self.log.debug("No Current State. Unable to undo.")
            return
        if not self._removed:
            self.log.debug("No properties removed. Unable to undo.")
            return

        try:
            for name in reversed(self._removed):
                current_value = self._current_value.get(name, self._null)
                if current_value is self._null:
                    continue
                self._cell.set_custom_property(name, current_value)
            self._removed.clear()

            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code")

    @override
    def undo(self) -> None:
        """
        Public method to undo the property deletions.

        Only performs undo if the original command was successful.
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
            CalcCell: The target cell instance.
        """
        return self._cell
