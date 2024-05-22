from __future__ import annotations
from typing import List, TYPE_CHECKING
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator


if TYPE_CHECKING:
    from .dialog_python import DialogPython


class DialogMenu:
    def __init__(self, dlg: DialogPython):
        self._dlg = dlg

    def get_popup_menu(self) -> PopupMenu:
        menu_data = self._get_menu_data()
        popup_creator = PopupCreator()
        popup_menu = popup_creator.create(menu_data)
        return popup_menu

    def _get_menu_data(self) -> List[dict]:
        rr = self._dlg.res_resolver.resolve_string

        new_menu = [
            {
                "text": rr("mnuData"),
                "command": ".uno.py_data",
                "submenu": [
                    {"text": rr("mnuValidate"), "command": ".uno:py_validate"},
                ],
            }
        ]
        return new_menu
