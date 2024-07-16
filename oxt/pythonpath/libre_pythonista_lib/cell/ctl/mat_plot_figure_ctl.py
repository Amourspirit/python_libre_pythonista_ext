from __future__ import annotations
from typing import Any, cast, Tuple
import uno
from ooodev.calc import CalcCell
from pathlib import Path

from ooodev.exceptions import ex as mEx
from ..props.key_maker import KeyMaker
from ...log.log_inst import LogInst
from ...ex import CellDeletedError
from .error_ctl import ErrorCtl

# from ..lpl_cell import LplCell
from ...code.py_source_mgr import PyInstance
from .cell_img import CellImg
from .shape_namer import ShapeNamer


class MatPlotFigureCtl:
    """
    A class to represent a pyc formula result rule.
    """

    def __init__(self, calc_cell: CalcCell) -> None:
        self.calc_cell = calc_cell
        self.key_maker = KeyMaker()
        self.is_deleted_cell = calc_cell.extra_data.get("deleted", False)
        self.log = LogInst()
        self._py_src = PyInstance(self.calc_cell.calc_doc)
        self.namer = ShapeNamer(self.calc_cell)
        self._prev_img = ""
        with self.log.indent(True):
            self.log.debug(f"CtlCellImg: __init__(): Entered")

    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_mp_figure

    def add_ctl(self) -> Any:
        """Add control to the cell"""
        with self.log.indent(True):
            src = self._py_src[self.calc_cell.cell_obj]
            dd = src.dd_data
            try:
                if self.is_deleted_cell:
                    raise CellDeletedError(f"Cell is deleted: {self.calc_cell.cell_obj}")
                # if self.log.is_debug:
                #     for k, v in dd.items():
                #         self.log.debug(f"src DotDict: {k}: {v}")
                if self._prev_img == dd.data:
                    self.log.debug("MatPlotFigureCtl: add_ctl(): No change in image. Not adding again.")
                    return
                self.remove_ctl()
                svg_path = Path(dd.data)
                if not svg_path.exists():
                    self.log.error(f"MatPlotFigureCtl: add_ctl(): File not found: {svg_path}")
                    return
                ci = CellImg(self.calc_cell, self.calc_cell.lo_inst)
                shp = ci.insert_cell_image_linked(svg_path)
                shp.name = self.namer.shape_name

                # self._set_ctl_script(ctl)
                self.log.debug("MatPlotFigureCtl: set_ctl_script(): Script set")
            except Exception:
                self.log.exception("MatPlotFigureCtl: set_ctl_script(): Error getting current control")

    def remove_ctl(self):
        """Remove control From the cell"""
        with self.log.indent(True):
            self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Entered")
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.namer.shape_name
                try:
                    shape = dp.find_shape_by_name(shape_name)
                    self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Found Shape: {shape_name}")
                    dp.remove(shape.component)  # type: ignore
                    self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Removed Shape: {shape_name}")
                    shape = None
                    self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Leaving")
                except mEx.ShapeMissingError:
                    self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Shape not found: {shape_name}")
                    self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Leaving")
                    return None

                if self.calc_cell.has_custom_property(self.key_maker.ctl_shape_key):
                    self.log.debug(
                        f"{self.__class__.__name__}: remove_ctl(): Removing custom {self.key_maker.ctl_shape_key}"
                    )
                    self.calc_cell.remove_custom_property(self.key_maker.ctl_shape_key)
                if self.calc_cell.has_custom_property(self.key_maker.ctl_orig_ctl_key):
                    self.log.debug(
                        f"{self.__class__.__name__}: remove_ctl(): Removing custom {self.key_maker.ctl_orig_ctl_key}"
                    )
                    self.calc_cell.remove_custom_property(self.key_maker.ctl_orig_ctl_key)

            except Exception as e:
                self.log.error(f"{self.__class__.__name__}: remove_ctl error: {e}", exc_info=True)
                return None

            # an error control may have been added. Remove it.
            try:
                self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Checking for error control.")
                err_ctl = ErrorCtl(self.calc_cell)
                err_ctl.remove_ctl()
            except Exception:
                self.log.debug(
                    f"{self.__class__.__name__}: remove_ctl(): Error removing error control. May not have been an error control to remove."
                )

    def update_ctl(self) -> None:
        """Updates the control. Usually set the controls size and pos."""
        pass

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
