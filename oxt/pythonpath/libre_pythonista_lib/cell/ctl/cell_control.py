from __future__ import annotations
from typing import Any, TYPE_CHECKING, Tuple
import contextlib
import uno
from com.sun.star.drawing import XControlShape
from com.sun.star.container import NoSuchElementException
from ooo.dyn.drawing.text_vertical_adjust import TextVerticalAdjust
from ooodev.calc.controls.sheet_control_base import SheetControlBase
from ooodev.calc.partial.calc_sheet_prop_partial import CalcSheetPropPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.exceptions import ex as mEx
from ooodev.loader import Lo
from ooodev.utils.helper.dot_dict import DotDict
from .ctl_namer import CtlNamer
from ...ex import CustomPropertyMissingError
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.sheet import Shape  # service
    from ooodev.calc.calc_cell import CalcCell
    from ooodev.loader.inst.lo_inst import LoInst
    from ooodev.calc.calc_form import CalcForm
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class CellControl(SheetControlBase):
    """A partial class for a cell control."""

    def __init__(self, calc_obj: CalcCell, lo_inst: LoInst | None = None) -> None:
        super().__init__(calc_obj, lo_inst)
        self._cfg = Config()
        self.__log = LogInst()
        self.__log.debug(f"CellControl: __init__(): Entered")

        self._form_name = f"Form_{self._cfg.general_code_name}"
        if not self.calc_obj.has_custom_property(self._cfg.cell_cp_codename):
            raise CustomPropertyMissingError(f"Custom Property not found: {self._cfg.cell_cp_codename}")
        self.namer = CtlNamer(self.calc_obj)
        self.__log.debug(f"CellControl: __init__(): Exit")

    def _init_calc_sheet_prop(self) -> None:
        CalcSheetPropPartial.__init__(self, self.calc_obj.calc_sheet)

    def _get_pos_size(self) -> Tuple[int, int, int, int]:
        ps = self.calc_obj.component.Position
        size = self.calc_obj.component.Size
        return (ps.X, ps.Y, size.Width, size.Height)

    def _get_form(self) -> CalcForm:
        sheet = self.calc_sheet
        if len(sheet.draw_page.forms) == 0:
            # insert a default user form so custom controls can be on a separate form
            sheet.draw_page.forms.add_form("Form1")
        if not sheet.draw_page.forms.has_by_name(self._form_name):
            sheet.draw_page.forms.add_form(self._form_name)
        return sheet.draw_page.forms.get_by_name(self._form_name)

    def _find_current_control(self) -> Any:
        self.__log.debug(f"CellControl: _find_current_control(): Entered")
        # pylint: disable=import-outside-toplevel
        cargs = CancelEventArgs(source=self)
        cargs.event_data = DotDict(
            control_name=self.namer.ctl_name, shape_name=self.namer.ctl_shape_name, cell=self.calc_obj
        )
        self.on_finding_control(cargs)
        if cargs.cancel:
            return None

        sheet = self.calc_sheet
        if not sheet.draw_page.forms.has_by_name(self._form_name):
            return None

        shape = None
        with contextlib.suppress(mEx.ShapeMissingError):
            shape = sheet.draw_page.find_shape_by_name(self.namer.ctl_shape_name)

        if shape is None:
            self.__log.debug(f"CellControl - _find_current_control(): Shape not found: {self.namer.ctl_shape_name}")
            return None

        x_shape = Lo.qi(XControlShape, shape.component)
        if x_shape is None:
            self.__log.debug(
                f"CellControl - _find_current_control(): XControlShape not found: {self.namer.ctl_shape_name}"
            )
            return None

        ctl = x_shape.getControl()
        if ctl is None:
            return None
        from ooodev.form.controls.from_control_factory import FormControlFactory

        factory = FormControlFactory(draw_page=sheet.draw_page.component, lo_inst=self.lo_inst)
        try:
            factory_ctl = factory.get_control_from_model(ctl)
            self.__log.debug(
                f"CellControl - _find_current_control(): Found Control from factory: {self.namer.ctl_name}"
            )
            return factory_ctl
        except NoSuchElementException:
            self.__log.warning(
                f"CellControl - _find_current_control() NoSuchElementException error from FormControlFactory Control not found: {self.namer.ctl_name}"
            )
            return None

    def _set_shape_props(self, shape: Shape) -> None:
        event_data = DotDict(
            Anchor=self.calc_obj.component,
            Decorative=False,
            HoriOrient=0,
            MoveProtect=True,
            Printable=False,
            ResizeWithCell=True,
            SizeProtect=False,
            TextVerticalAdjust=TextVerticalAdjust.CENTER,
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

    @property
    def calc_obj(self) -> CalcCell:
        return super().calc_obj
