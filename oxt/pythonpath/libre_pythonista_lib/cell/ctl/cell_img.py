from __future__ import annotations
from typing import Any, TYPE_CHECKING, Tuple
import contextlib

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
from com.sun.star.drawing import XShape
from ooodev.calc.controls.sheet_control_base import SheetControlBase
from ooodev.calc.partial.calc_sheet_prop_partial import CalcSheetPropPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.exceptions import ex as mEx
from ooodev.loader import Lo
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.kind.drawing_shape_kind import DrawingShapeKind
from ooodev.units import UnitMM100
from .shape_namer import ShapeNamer
from ...ex import CustomPropertyMissingError
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from ooodev.calc import CalcCell, CalcSheet
    from ooodev.loader.inst.lo_inst import LoInst
    from ooodev.calc.calc_form import CalcForm
    from ooodev.utils.type_var import PathOrStr
    from ooodev.calc import SpreadsheetDrawPage
    from ooodev.draw.shapes.draw_shape import DrawShape
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class CellImg(SheetControlBase):
    """A partial class for a cell control."""

    def __init__(self, calc_obj: CalcCell, lo_inst: LoInst | None = None) -> None:
        super().__init__(calc_obj, lo_inst)
        self._cfg = Config()
        self.__log = LogInst()
        with self.__log.indent(True):
            self.__log.debug(f"CellControl: __init__(): Entered")

            self._form_name = f"Form_{self._cfg.general_code_name}"
            if not self.calc_obj.has_custom_property(self._cfg.cell_cp_codename):
                raise CustomPropertyMissingError(f"Custom Property not found: {self._cfg.cell_cp_codename}")
            self.namer = ShapeNamer(self.calc_obj)
            self.__log.debug(f"CellControl: __init__(): Exit")

    def _init_calc_sheet_prop(self) -> None:
        CalcSheetPropPartial.__init__(self, self.calc_obj.calc_sheet)

    @override
    def _get_pos_size(self) -> Tuple[UnitMM100, UnitMM100, UnitMM100, UnitMM100]:  # type: ignore
        if self.calc_obj.component.IsMerged:  # type: ignore
            self.__log.debug(f"CellControl: _get_pos_size(): Cell is merged")
            cursor = self.calc_obj.calc_sheet.create_cursor_by_range(cell_obj=self.calc_obj.cell_obj)
            cursor.component.collapseToMergedArea()
            rng = cursor.get_calc_cell_range()
            ps = rng.component.Position
            size = rng.component.Size
        else:
            self.__log.debug(f"CellControl: _get_pos_size(): Cell is not merged")
            ps = self.calc_obj.component.Position
            size = self.calc_obj.component.Size
        return (UnitMM100(ps.X), UnitMM100(ps.Y), UnitMM100(size.Width), UnitMM100(size.Height))

    @override
    def _get_form(self) -> CalcForm:
        sheet = self.calc_sheet
        if len(sheet.draw_page.forms) == 0:
            # insert a default user form so custom controls can be on a separate form
            sheet.draw_page.forms.add_form("Form1")
        if not sheet.draw_page.forms.has_by_name(self._form_name):
            sheet.draw_page.forms.add_form(self._form_name)
        return sheet.draw_page.forms.get_by_name(self._form_name)

    @override
    def _find_current_control(self) -> Any:
        with self.__log.indent(True):
            self.__log.debug(f"CellControl: _find_current_control(): Entered")
            # pylint: disable=import-outside-toplevel
            cargs = CancelEventArgs(source=self)
            cargs.event_data = DotDict(shape_name=self.namer.shape_name, cell=self.calc_obj)
            self.on_finding_control(cargs)
            if cargs.cancel:
                return None

            sheet = self.calc_sheet
            if not sheet.draw_page.forms.has_by_name(self._form_name):
                return None

            shape = None
            with contextlib.suppress(mEx.ShapeMissingError):
                shape = sheet.draw_page.find_shape_by_name(self.namer.shape_name)

            if shape is None:
                self.__log.debug(f"CellControl - _find_current_control(): Shape not found: {self.namer.shape_name}")
                return None

            x_shape = Lo.qi(XShape, shape.component)
            return x_shape

    @override
    def _set_shape_props(self, shape: XShape) -> None:
        event_data = DotDict(
            Anchor=self.calc_obj.component,
            Decorative=False,
            HoriOrient=0,
            MoveProtect=True,
            Printable=False,
            ResizeWithCell=True,
            SizeProtect=False,
            Visible=True,
        )
        eargs = CancelEventArgs(source=shape)
        eargs.event_data = event_data
        self.on_setting_shape_props(eargs)
        if eargs.cancel:
            return
        for key, value in eargs.event_data.items():
            if hasattr(shape, key):
                setattr(shape, key, value)

    def insert_cell_image_linked(self, fmn: PathOrStr) -> DrawShape[SpreadsheetDrawPage[CalcSheet]]:
        sheet = self.calc_sheet
        shape = sheet.draw_page.add_shape(DrawingShapeKind.GRAPHIC_OBJECT_SHAPE, *self._get_pos_size())
        shape.set_image(fmn)
        self.__log.debug(f"CellImg: insert_cell_image_linked(): Image set  {fmn}")
        self._set_shape_props(shape.component)
        return shape

    @property
    def calc_obj(self) -> CalcCell:
        return super().calc_obj
