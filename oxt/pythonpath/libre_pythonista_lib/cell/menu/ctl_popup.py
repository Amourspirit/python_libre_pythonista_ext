from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator

from ...res.res_resolver import ResResolver
from ...dispatch.cell_dispatch_state import CellDispatchState
from ..props.key_maker import KeyMaker
from ...const import UNO_DISPATCH_CODE_EDIT, UNO_DISPATCH_DF_STATE, UNO_DISPATCH_CODE_DEL
from ..state.state_kind import StateKind
from ..state.ctl_state import CtlState

if TYPE_CHECKING:
    from com.sun.star.awt import MenuEvent
    from ooodev.events.args.event_args import EventArgs


def on_menu_select(src: Any, event: EventArgs, menu: PopupMenu) -> None:
    # print("Menu Selected")
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
        self._key_maker = KeyMaker()
        self._ctl_state = CtlState(self._cell)

    def _get_state_menu(self) -> list:
        global UNO_DISPATCH_DF_STATE
        # key = self._key_maker.ctl_state_key
        # if not self._cell.has_custom_property(key):
        #     return []
        # state = self._cell.get_custom_property(key)
        state = self._ctl_state.get_state()
        cmd = UNO_DISPATCH_DF_STATE
        edit_uno = f"{cmd}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        py_obj = self._res.resolve_string("mnuViewPyObj")  # Python Object
        array = self._res.resolve_string("mnuViewArray")  # Array
        return [
            {
                "text": "State",
                "command": "",
                "submenu": [
                    {"text": py_obj, "command": edit_uno, "enabled": state == StateKind.ARRAY},
                    {"text": array, "command": edit_uno, "enabled": state == StateKind.PY_OBJ},
                ],
            },
        ]

    def _get_popup_menu(self) -> list:
        global UNO_DISPATCH_CODE_EDIT
        edit_name = self._res.resolve_string("mnuEditCode")  # Edit Menu
        del_name = self._res.resolve_string("mnuDeletePyCell")  # Delete Python
        cps = CellDispatchState(cell=self._cell)
        cmd_enabled = cps.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT)
        edit_url = f"{UNO_DISPATCH_CODE_EDIT}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        del_url = f"{UNO_DISPATCH_CODE_DEL}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        new_menu = [
            {"text": edit_name, "command": edit_url, "enabled": cmd_enabled},
            {"text": del_name, "command": del_url, "enabled": cmd_enabled},
        ]
        if self._cell.get_custom_property(self._key_maker.cell_array_ability_key, False):
            state_menu = self._get_state_menu()
            if state_menu:
                new_menu.extend(state_menu)
        return new_menu

    def get_menu(self) -> PopupMenu:
        creator = PopupCreator()
        pm = creator.create(self._get_popup_menu())
        # pm.add_event_item_selected(on_menu_select)
        pm.subscribe_all_item_selected(on_menu_select)
        return pm
