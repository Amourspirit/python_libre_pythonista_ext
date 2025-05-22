from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.style.default_style import DefaultStyle
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.style.default_style import DefaultStyle
    from libre_pythonista_lib.style.style_t import StyleT
    from libre_pythonista_lib.utils.custom_ext import override


class CmdCellRemoveBorderStyle(CmdBase, LogMixin, CmdCellCtlT):
    def __init__(self, cell: CalcCell, style: Union[StyleT, None] = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        if style is None:
            style = DefaultStyle()
        self._style = style
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    @override
    def execute(self) -> None:
        self.success = False
        try:
            self.cell.style_borders_clear()
        except Exception:
            self.log.exception("Error setting cell Code")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_cell_add_border_style import (
                    CmdCellAddBorderStyle,
                )
            else:
                from libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_cell_add_border_style import (
                    CmdCellAddBorderStyle,
                )
            cmd = CmdCellAddBorderStyle(cell=self.cell, style=self._style)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute undo command.")
                return
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
