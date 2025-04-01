from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.format.calc.direct.cell.borders import Side, Shadow
from ooodev.format.inner.direct.structs.side import LineSize

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


class CmdCellAddBorderStyle(CmdBase, LogMixin, CmdCellCtlT):
    def __init__(self, cell: CalcCell, style: StyleT | None = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        if style is None:
            style = DefaultStyle()
        self._style = style
        self._cell = cell

    def _get_border_side(self) -> Side:
        side = Side(color=self._style.color_border, width=LineSize.VERY_THIN)
        return side

    def _get_border_shadow(self) -> Shadow:
        shadow = Shadow(color=self._style.color_shadow, width=1)
        return shadow

    def _add_style_cell(self) -> None:
        """Formats a cell range."""
        self.cell.style_borders(border_side=self._get_border_side(), shadow=None)

    @override
    def execute(self) -> None:
        self.success = False
        try:
            self._add_style_cell()
        except Exception:
            self.log.exception("Error setting cell Code")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            self.cell.style_borders_clear()
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
