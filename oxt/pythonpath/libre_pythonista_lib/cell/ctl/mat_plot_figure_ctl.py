from __future__ import annotations
from typing import Any, cast, Tuple
from ooodev.calc import CalcCell

try:
    from ...convert.data_convertors.matplot_convertor import fig_to_svg
except ImportError:
    MatPlotConvertor = None

from ..props.key_maker import KeyMaker
from ...log.log_inst import LogInst
from .cell_img import CellImg


class MatPlotFigureCtl:
    """
    A class to represent a pyc formula result rule.
    """

    def __init__(self, calc_cell: CalcCell) -> None:
        self.calc_cell = calc_cell
        self.key_maker = KeyMaker()
        self.log = LogInst()
        with self.log.indent(True):
            self.log.debug(f"CtlCellImg: __init__(): Entered")

    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_cell_img

    def add_ctl(self) -> Any:
        """Add control to the cell"""
        with self.log.indent(True):
            if MatPlotConvertor is None:
                self.log.error("MatPlotFigureCtl: add_ctl(): MatPlotConvertor not found")
                return
            try:
                svg_path = fig_to_svg()
                ci = CellImg(self.calc_cell, self.calc_cell.lo_inst)
                ci.insert_cell_image_linked(svg_path)

                # self._set_ctl_script(ctl)
                self.log.debug("SimpleCtl: set_ctl_script(): Script set")
            except Exception:
                self.log.exception("SimpleCtl: set_ctl_script(): Error getting current control")

    def remove_ctl(self):
        """Remove control From the cell"""
        with self.log.indent(True):
            if MatPlotConvertor is None:
                self.log.error("MatPlotFigureCtl: add_ctl(): MatPlotConvertor not found")
                return

    def update_ctl(self) -> None:
        """Updates the control. Usually set the controls size and pos."""
        with self.log.indent(True):
            if MatPlotConvertor is None:
                self.log.error("MatPlotFigureCtl: add_ctl(): MatPlotConvertor not found")
                return

    def get_cell_pos_size(self) -> Tuple[int, int, int, int]:
        """
        Gets the position and size of the control.

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) in  ``1/100th mm``.
        """
        ps = self.calc_cell.component.Position
        size = self.calc_cell.component.Size
        return (ps.X, ps.Y, size.Width, size.Height)

    def update_ctl_action(self) -> None:
        """
        Updates the controls action such as setting ``actionPerformed`` macro.
        """
        pass
