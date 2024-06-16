from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator
from ...res.res_resolver import ResResolver

if TYPE_CHECKING:
    from com.sun.star.awt import MenuEvent
    from ooodev.events.args.event_args import EventArgs


def on_menu_select(src: Any, event: EventArgs, menu: PopupMenu) -> None:
    print("Menu Selected")
    me = cast("MenuEvent", event.event_data)
    command = menu.get_command(me.MenuId)
    if command:
        # check if command is a dispatch command
        if menu.is_dispatch_cmd(command):
            menu.execute_cmd(command)


class CtlPopup:

    def __init__(self, cell: CalcCell) -> None:
        self._cell = cell
        self._res = ResResolver()
        self._sheet_name = self._cell.calc_sheet.name

    def _get_popup_menu(self) -> list:
        edit_name = self._res.resolve_string("mnuEditCode")  # Edit Menu
        edit_uno = f".uno:libre_pythonista.calc.menu.code.edit?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        new_menu = [{"text": edit_name, "command": edit_uno}]
        return new_menu

    def get_menu(self) -> PopupMenu:
        creator = PopupCreator()
        pm = creator.create(self._get_popup_menu())
        pm.add_event_item_selected(on_menu_select)
        return pm
