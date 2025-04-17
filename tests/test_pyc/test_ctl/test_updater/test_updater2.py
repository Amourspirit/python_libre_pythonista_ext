from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

import contextlib
from typing import cast, Tuple, TYPE_CHECKING

from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point
from com.sun.star.awt import XActionListener

from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.exceptions import ex as mEx  # noqa: N812
from ooodev.utils.color import StandardColor
from ooodev.units import UnitMM100
from ooodev.utils.kind.language_kind import LanguageKind


@pytest.fixture(scope="function")
def control_props():  # noqa: ANN201
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind
    return (
        CtlPropKind.CTL_SHAPE,
        CtlPropKind.CTL_ORIG,
        CtlPropKind.PYC_RULE,
        CtlPropKind.MODIFY_TRIGGER_EVENT,
    )


@pytest.fixture(scope="function")
def config():  # noqa: ANN001, ANN201
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind

    class Config:
        def __init__(self) -> None:
            self.is_shared_installed = False
            self.cell_cp_prefix = "cell_cp_prefix"
            self.oxt_name = "LibrePythonista"
            self.py_script_sheet_ctl_click = "sheet_ctl_click"
            self.macro_lp_sheet_ctl_click = "macro_lp_sheet_ctl_click"

    def wrapper():  # noqa: ANN202
        return Config()

    return wrapper


@pytest.fixture(scope="function")
def cell_control():  # noqa: ANN001, ANN201
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind

    class CellControl:
        def __init__(self, cell, lo_inst) -> None:
            self.cell = cell
            self.current_control = object()
            self._controls = {}

        def insert_control_button(self, label: str, name: str):  # noqa: ANN202
            self._controls[name] = label
            model = DotDict(BackgroundColor=StandardColor.RED)
            ctl_shape = DotDict(name=name, label=label)
            return DotDict(control_shape=ctl_shape, model=model, tab_stop=False, printable=False)

    def wrapper(cell, lo_inst):  # noqa: ANN001, ANN202
        return CellControl(cell, lo_inst)

    return wrapper


@pytest.fixture(scope="function")
def calc_draw_page_shape():  # noqa: ANN001, ANN201
    class CalcDrawPageShape:
        def __init__(self) -> None:
            self.component = {"Component": None}
            self._size = None
            self._position = None

        def setSize(self, size: Size) -> None:  # noqa: N802
            self._size = size

        def setPosition(self, point: Point) -> None:  # noqa: N802
            self._position = point

    def wrapper() -> CalcDrawPageShape:
        return CalcDrawPageShape()

    return wrapper


@pytest.fixture(scope="function")
def calc_draw_page(calc_draw_page_shape):  # noqa: ANN001, ANN201
    class CalcDrawPage:
        def __init__(self) -> None:
            self.shape = calc_draw_page_shape()

        def find_shape_by_name(self, shape_name: str) -> object:
            if shape_name == "" or shape_name == "error":
                raise mEx.ShapeMissingError("Shape not found")
            return {"shape": shape_name}

    def wrapper() -> CalcDrawPage:
        return CalcDrawPage()

    return wrapper


@pytest.fixture(scope="function")
def calc_sheet(calc_draw_page):  # noqa: ANN001, ANN201
    class CalcSheet:
        def __init__(self) -> None:
            self.draw_page = calc_draw_page()

    def wrapper() -> CalcSheet:
        return CalcSheet()

    return wrapper


@pytest.fixture(scope="function")
def calc_cell(control_props, config, calc_sheet, build_setup, loader):  # noqa: ANN001, ANN201
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
    else:
        from libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind

    class CalcCell:
        def __init__(self) -> None:
            self.extra_data = {}
            self.calc_sheet = calc_sheet()
            self.lo_inst = None
            self.component = DotDict(Position=Point(10, 10), Size=Size(100, 100))
            self._ctl_props = control_props
            self._supported_props = []
            self._cfg = config()
            for prop in control_props:
                self._supported_props.append(self._get_prop_key_value(prop))

        def _get_prop_key_value(self, prop_kind: CtlPropKind) -> str:
            """
            Gets a custom property value from the cell.

            Args:
                key (CtlPropKind): Custom property key.

            Returns:
                Any: Value of the custom property.
            """
            return f"{self._cfg.cell_cp_prefix}{prop_kind.value}"

        def has_custom_property(self, key: str) -> bool:
            return key in self._supported_props

        def remove_custom_property(self, key: str) -> None:
            self._supported_props.remove(key)

        def set_custom_property(self, key: str, value: Any) -> None:  # noqa: ANN401
            self._supported_props.append(key)

    def wrapper() -> CalcCell:
        return CalcCell()

    return wrapper


@pytest.fixture(scope="function")
def control_class(calc_cell, control_props):  # noqa: ANN001, ANN201
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.kind.ctl_kind import CtlKind

    class Ctl:
        def __init__(self, calc_cell) -> None:
            self.calc_cell = calc_cell
            self.ctl_props = control_props
            self.control_kind = CtlKind.STRING
            self.ctl_name = "ctl_name"
            self.ctl_shape_name = "ctl_shape_name"
            self.label = "<>"
            self.code_name = "code_name"

        def get_label(self) -> str:
            """Gets the control label such as ``<>``."""
            return self.label

        def supports_prop(self, prop: CtlPropKind) -> bool:
            """Checks if the control supports the given property."""
            return prop in self.ctl_props

    def wrapper():
        return Ctl(calc_cell())

    return wrapper


@pytest.fixture(scope="function")
def provider(control_class, config, cell_control):  # noqa: ANN001, ANN201
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.mixin.calc_cell_mixin import CalcCellMixin
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider import CtlProvider
        from typing_extensions import override
        from com.sun.star.drawing import ControlShape  # service
        from ooodev.form.controls.form_ctl_base import FormCtlBase
        from oxt.pythonpath.libre_pythonista_lib.ex.exceptions import CellDeletedError
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_t import CtlT

        from oxt.pythonpath.libre_pythonista_lib.const.event_const import (
            CONTROL_ADDED,
            CONTROL_REMOVED,
            CONTROL_REMOVING,
            CONTROL_ADDING,
            CONTROL_UPDATING,
            CONTROL_UPDATED,
        )
    else:
        from libre_pythonista_lib.pyc.cell.ctl.ctl_prop_kind import CtlPropKind

        from libre_pythonista_lib.pyc.cell.ctl.mixin.calc_cell_mixin import CalcCellMixin
        from libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider import CtlProvider
        from libre_pythonista_lib.ex.exceptions import CellDeletedError

        from libre_pythonista_lib.const.event_const import (
            CONTROL_ADDED,
            CONTROL_REMOVED,
            CONTROL_REMOVING,
            CONTROL_ADDING,
            CONTROL_UPDATING,
            CONTROL_UPDATED,
        )

        def override(f) -> object:  # noqa: ANN001
            return f

    class CtlProviderTest(CtlProvider, CalcCellMixin):
        """Default Control Provider"""

        @override
        def __init__(self, ctl: CtlT) -> None:
            CtlProvider.__init__(self, ctl)
            CalcCellMixin.__init__(self, ctl.calc_cell)
            self._cfg = config()
            self.is_deleted_cell = ctl.calc_cell.extra_data.get("deleted", False)
            self._script_name = f"{self._cfg.oxt_name}.oxt|python|scripts|{self._cfg.py_script_sheet_ctl_click}"
            self._script_loc = f"{self._script_name}${self._cfg.macro_lp_sheet_ctl_click}"

        @override
        def add_ctl(self) -> object | None:
            # There are bugs when accessing controls on sheets.
            # see: https://bugs.documentfoundation.org/show_bug.cgi?id=159134
            # Controls can lose there models when switched to a different sheet and back.
            # For this reason we only return the shape from them method.
            # Shape.getControl() can be used if necessary.,
            try:
                cargs = CancelEventArgs(self)
                dd = DotDict(cell=self.calc_cell, control=self)
                cargs.event_data = dd
                self.trigger_event(CONTROL_ADDING, cargs)
                if cargs.cancel:
                    return

                if self.is_deleted_cell:
                    raise CellDeletedError(f"Cell is deleted: {self.calc_cell.cell_obj}")

                # check for the shape on the draw page.
                # If for some reason the control in not found it is possible a shape was there.
                # In this case we need to remove the shape.
                with contextlib.suppress(mEx.ShapeMissingError):
                    sheet = self.calc_cell.calc_sheet
                    dp = sheet.draw_page
                    shape_name = self.ctl.ctl_shape_name
                    shape = dp.find_shape_by_name(shape_name)
                    self.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
                    return shape.component

                name = self.ctl.ctl_name
                cell_ctl = cell_control(self.calc_cell, self.calc_cell.lo_inst)
                btn = cell_ctl.insert_control_button(label=self.ctl.get_label(), name=name)
                shape = btn.control_shape

                self._set_size(shape)
                btn.printable = False
                btn.model.BackgroundColor = self._get_button_bg_color()  # type: ignore
                btn.tab_stop = False
                self._set_ctl_script(btn)
                if self.ctl.supports_prop(CtlPropKind.CTL_SHAPE):
                    self.calc_cell.set_custom_property(
                        self._get_prop_key_value(CtlPropKind.CTL_SHAPE), self.ctl.ctl_shape_name
                    )
                if self.ctl.supports_prop(CtlPropKind.CTL_ORIG):
                    self.calc_cell.set_custom_property(
                        self._get_prop_key_value(CtlPropKind.CTL_ORIG), str(self.ctl.control_kind)
                    )
                self.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
                return shape
            except Exception as e:
                return None

        @override
        def update_ctl_action(self) -> None:
            try:
                cargs = CancelEventArgs(self)

                cell_ctl = cell_control(self.calc_cell, self.calc_cell.lo_inst)
                ctl = cast("FormCtlBase", cell_ctl.current_control)
                dd = DotDict(cell=self.calc_cell, cell_control=cell_ctl, ctl=ctl, control=self)
                cargs.event_data = dd
                self.trigger_event(CONTROL_UPDATING, cargs)
                if cargs.cancel:
                    return
                if ctl is None:
                    return
                # self._remove_ctl_script(ctl)
                self._set_ctl_script(ctl)
                self.trigger_event(CONTROL_UPDATED, EventArgs.from_args(cargs))
            except Exception:
                raise

        @override
        def update_ctl(self) -> None:
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.ctl.ctl_shape_name
                cargs = CancelEventArgs(self)
                dd = DotDict(cell=self.calc_cell, shape_name=shape_name, control=self)
                cargs.event_data = dd
                self.trigger_event(CONTROL_UPDATING, cargs)
                if cargs.cancel:
                    return
                try:
                    shape = dp.find_shape_by_name(shape_name)
                    self._set_size(shape.component)  # type: ignore
                except mEx.ShapeMissingError:
                    pass
                self.trigger_event(CONTROL_UPDATED, EventArgs.from_args(cargs))
            except Exception as e:
                return None

        @override
        def remove_ctl(self) -> None:
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.ctl.ctl_shape_name

                cargs = CancelEventArgs(self)
                dd = DotDict(cell=self.calc_cell, shape_name=shape_name, control=self)
                cargs.event_data = dd
                self.trigger_event(CONTROL_REMOVING, cargs)
                if cargs.cancel:
                    return
                try:
                    shape = dp.find_shape_by_name(shape_name)
                    dp.remove(shape.component)  # type: ignore
                    shape = None
                except mEx.ShapeMissingError:
                    pass

                if self.ctl.supports_prop(CtlPropKind.CTL_SHAPE):
                    prop_key = self._get_prop_key_value(CtlPropKind.CTL_SHAPE)
                    if self.calc_cell.has_custom_property(prop_key):
                        self.calc_cell.remove_custom_property(prop_key)
                if self.ctl.supports_prop(CtlPropKind.CTL_ORIG):
                    prop_key = self._get_prop_key_value(CtlPropKind.CTL_SHAPE)
                    if self.calc_cell.has_custom_property(prop_key):
                        self.calc_cell.remove_custom_property(prop_key)
                self.trigger_event(CONTROL_REMOVED, EventArgs.from_args(cargs))
            except Exception as e:
                return None

        def get_cell_pos_size(self) -> Tuple[int, int, int, int]:
            """
            Gets the position and size of the control.

            Returns:
                Tuple[int, int, int, int]: (x, y, width, height) in  ``1/100th mm``.
            """
            ps = self.calc_cell.component.Position
            size = self.calc_cell.component.Size
            return (ps.X, ps.Y, size.Width, size.Height)

        def _get_button_bg_color(self) -> int:
            return StandardColor.TEAL_LIGHT3

        def _set_size(self, shape: ControlShape) -> None:
            x, y, width, height = self.get_cell_pos_size()
            # sz = shape.getSize()
            new_sz = Size(min(height, int(UnitMM100(455))), height)
            # new_sz = Size(sz.Height, sz.Height)
            shape.setSize(new_sz)
            shape.setPosition(Point(x, y))

        def _set_ctl_script(self, ctl: FormCtlBase) -> None:
            """
            Sets the actionPerformed script location for the control.

            Args:
                ctl (FormCtlBase): Control that has a actionPerformed method.
            """
            location = "share:uno_packages" if self._cfg.is_shared_installed else "user:uno_packages"
            ctl.assign_script(
                interface_name=XActionListener,  # type: ignore
                method_name="actionPerformed",
                script_name=self._script_loc,
                loc=location,
                language=LanguageKind.PYTHON,
                auto_remove_existing=True,
            )

        def _get_prop_key_value(self, prop_kind: CtlPropKind) -> str:
            """
            Gets a custom property value from the cell.

            Args:
                key (CtlPropKind): Custom property key.

            Returns:
                Any: Value of the custom property.
            """
            return f"{self._cfg.cell_cp_prefix}{prop_kind.value}"

    def wrapper() -> CtlProviderTest:
        return CtlProviderTest(control_class())

    return wrapper


def test_updater(provider) -> None:
    p = provider()
    assert p is not None
    p.add_ctl()
    p.ctl.ctl_shape_name = "error"
    p.add_ctl()
