from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import uno

from .run_time_dialog_base import RuntimeDialogBase

from com.sun.star.awt import Selection  # struct

if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlEdit  # service


class NameInput(RuntimeDialogBase):
    """Input dialog."""

    MARGIN = 3
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 26
    HEIGHT = MARGIN * 3 + BUTTON_HEIGHT * 2
    WIDTH = 300
    EDIT_NAME = "edit_name"

    def __init__(self, ctx: Any, title: str, default: str = "", parent: Any = None):
        super().__init__(ctx)
        self.title = title
        self.default = default
        self.parent = parent
        self._is_init = False

    def _init(self):
        if self._is_init:
            return
        margin = self.MARGIN
        self.create_dialog(self.title, size=(self.WIDTH, self.HEIGHT))
        self.create_edit(
            self.EDIT_NAME,
            pos=(margin, margin),
            size=(self.WIDTH - margin * 2, self.BUTTON_HEIGHT),
            prop_names=("HideInactiveSelection", "Text"),
            prop_values=(True, self.default),
        )
        self.create_button(
            "btn_ok",
            "ok",
            pos=(self.WIDTH - self.BUTTON_WIDTH * 2 - margin * 2, self.BUTTON_HEIGHT + margin * 2),
            size=(self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
            prop_names=("DefaultButton", "Label", "PushButtonType"),
            prop_values=(True, "OK", 1),
        )
        self.create_button(
            "btn_cancel",
            "cancel",
            pos=(self.WIDTH - self.BUTTON_WIDTH - margin, self.BUTTON_HEIGHT + margin * 2),
            size=(self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
            prop_names=("Label", "PushButtonType"),
            prop_values=("Cancel", 2),
        )
        self.set_focus(self.EDIT_NAME)
        if self.parent:
            self.dialog.createPeer(self.parent.getToolkit(), self.parent)
        if self.default:
            edit_ctl = cast("UnoControlEdit", self.get(self.EDIT_NAME))
            edit_ctl.setSelection(Selection(0, len(self.default)))
        self._is_init = True

    def _result(self):
        return self.get_text("edit_name")
