from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ
from ooodev.draw.shapes import DrawShape
from ooodev.calc import CalcSheet, SpreadsheetDrawPage


if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.draw_page.qry_shape_by_name import QryShapeByName

else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.qry.calc.sheet.draw_page.qry_shape_by_name import QryShapeByName


class CmdDelShapeByName(CmdBase, LogMixin, CmdSheetT):
    """Command that deletes a shape from a sheet's draw page by its name."""

    def __init__(self, sheet: CalcSheet, shape_name: str) -> None:
        """
        Initialize the command.

        Args:
            sheet: The sheet containing the shape to delete
            shape_name: Name of the shape to delete
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SHEET
        self._sheet = sheet
        self._shape_name = shape_name
        self._current = cast(DrawShape[SpreadsheetDrawPage[CalcSheet]] | None, NULL_OBJ)

    def _qry_shape(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]] | None:
        """Query the shape to be deleted by its name."""
        qry = QryShapeByName(sheet=self._sheet, shape_name=self._shape_name)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Execute the command to delete the shape.
        Sets success to True if shape is deleted or doesn't exist.
        """
        self.success = False
        try:
            if self._current is NULL_OBJ:
                self._current = self._qry_shape()
            if self._current is None:
                self.log.debug("Shape not found. Nothing to do.")
                self.success = True
                return
            dp = self._sheet.draw_page
            dp.remove(self._current.component)

        except Exception:
            self.log.exception("Error executing command")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """Internal method to undo the shape deletion by adding it back."""
        try:
            if not self._current:
                return
            dp = self._sheet.draw_page
            dp.add(self._current.component)
            self._current = cast(None, NULL_OBJ)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing command")

    @override
    def undo(self) -> None:
        """
        Undo the command if it was successful.
        Restores the previously deleted shape.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def sheet(self) -> CalcSheet:
        """Get the sheet associated with this command."""
        return self._sheet
