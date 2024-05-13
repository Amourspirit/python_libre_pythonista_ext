from __future__ import annotations
from typing import Any, Tuple, Sequence, TYPE_CHECKING, cast
import uno

from .dialog_base import DialogBase
from ..lo_util.resource_resolver import ResourceResolver

from com.sun.star.awt.PosSize import POS, SIZE, POSSIZE  # type: ignore
from com.sun.star.beans import PropertyValue  # struct
from com.sun.star.awt import XActionListener
from com.sun.star.awt import XControl


if TYPE_CHECKING:
    from com.sun.star.form.control import CommandButton  # service
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlDialogModel  # service

    # from com.sun.star.beans import XPropertyAccess
    from com.sun.star.beans import XMultiPropertySet
    from com.sun.star.awt import XWindow


class RuntimeDialogBase(DialogBase):
    """Runtime dialog base."""

    def __init__(self, ctx: Any):
        super().__init__(ctx)
        self._dialog = cast("UnoControlDialog", None)

    def _result(self):
        """Returns result."""
        return None

    def _init(self):
        """Initialize, create dialog and controls."""
        raise NotImplementedError

    def execute(self) -> Any:
        """
        Execute to show this dialog.
        None return value should mean canceled.
        """
        self._init()
        result = self._result() if self.dialog.execute() else None
        self.dialog.dispose()
        return result

    def create_control(
        self,
        name: str,
        type_: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        prop_names: Sequence[str] | None = None,
        prop_values: Sequence[Any] | None = None,
        full_name: bool = False,
    ):
        """Create and insert control."""
        if not full_name:
            type_ = f"com.sun.star.awt.UnoControl{type_}Model"
        dialog_model = cast("UnoControlDialogModel", self.dialog.getModel())
        model = cast("XMultiPropertySet", dialog_model.createInstance(type_))
        if prop_names and prop_values:
            # properties = self.convert_to_property_values(prop_names, prop_values)
            # model.setPropertyValues(properties)
            model.setPropertyValues(tuple(prop_names), tuple(prop_values))
        dialog_model.insertByName(name, model)
        ctrl = cast("XWindow", self.dialog.getControl(name))
        ctrl.setPosSize(pos[0], pos[1], size[0], size[1], POSSIZE)
        return ctrl

    def convert_to_property_values(
        self, prop_names: Sequence[str], prop_values: Sequence[Any]
    ) -> Tuple[PropertyValue, ...]:
        """Convert to PropertyValue."""
        if not prop_names:
            return ()
        if len(prop_names) != len(prop_values):
            raise ValueError("prop_names and prop_values must have same length.")
        return tuple(PropertyValue(Name=name, Value=value) for name, value in zip(prop_names, prop_values))

    def create_dialog(
        self,
        title: str,
        *,
        pos: Tuple[int, int] | None = None,
        size: Tuple[int, int] | None = None,
        parent: Any = None,
        prop_names: Sequence[str] | None = None,
        prop_values: Sequence[Any] | None = None,
    ):
        """Create base dialog."""
        dialog = cast("UnoControlDialog", self.create("com.sun.star.awt.UnoControlDialog"))
        dialog_model = cast("UnoControlDialogModel", self.create("com.sun.star.awt.UnoControlDialogModel"))
        dialog_model.ResourceResolver = ResourceResolver(self.ctx).resource_resolver  # type: ignore
        dialog.setModel(dialog_model)
        dialog.setVisible(False)
        dialog.setTitle(title)

        if isinstance(size, tuple) and len(size) == 2:
            dialog.setPosSize(0, 0, size[0], size[1], SIZE)
        if isinstance(pos, tuple) and len(pos) == 2:
            dialog.setPosSize(pos[0], pos[1], 0, 0, POS)
        if prop_names and prop_values and len(prop_names) == len(prop_values):
            dialog_model.setPropertyValues(tuple(prop_names), tuple(prop_values))

        self._dialog = dialog

    def create_label(
        self,
        name: str,
        command: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        prop_names: Sequence[str] | None = None,
        prop_values: Sequence[Any] | None = None,
        action: XActionListener | None = None,
    ):
        """Create and add new label."""
        self.create_control(name, "FixedText", pos, size, prop_names, prop_values)

    def create_button(
        self,
        name,
        command: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        prop_names: Sequence[str] | None = None,
        prop_values: Sequence[Any] | None = None,
        action: XActionListener | None = None,
    ):
        """Create and add new button."""
        btn = cast("CommandButton", self.create_control(name, "Button", pos, size, prop_names, prop_values))
        btn.setActionCommand(command)
        if action:
            btn.addActionListener(action)

    def create_edit(
        self,
        name: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        prop_names: Sequence[str] | None = None,
        prop_values: Sequence[Any] | None = None,
    ):
        """Create and add new edit control."""
        self.create_control(name, "Edit", pos, size, prop_names, prop_values)

    def create_tree(
        self,
        name: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        prop_names: Sequence[str] | None = None,
        prop_values: Sequence[Any] | None = None,
    ):
        """Create and add new tree."""
        self.create_control(
            name, "com.sun.star.awt.tree.TreeControlModel", pos, size, prop_names, prop_values, full_name=True
        )

    def get(self, name: str) -> XControl:
        """Returns specified control by name."""
        return self.dialog.getControl(name)

    def get_text(self, name: str) -> str:
        """Returns value of Text attribute specified by name."""
        return self.dialog.getControl(name).getModel().Text  # type: ignore

    def set_focus(self, name: str):
        """Set focus to the control specified by the name."""
        window = cast("XWindow", self.dialog.getControl(name))
        window.setFocus()

    @property
    def dialog(self) -> UnoControlDialog:
        """Returns dialog."""
        if not self._dialog:
            self._init()
        return self._dialog
