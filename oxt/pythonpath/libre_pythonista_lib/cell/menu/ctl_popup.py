from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator

from ...res.res_resolver import ResResolver
from ...dispatch.cell_dispatch_state import CellDispatchState
from ..props.key_maker import KeyMaker
from ...const import UNO_DISPATCH_CODE_EDIT, UNO_DISPATCH_CODE_DEL, UNO_DISPATCH_CELL_SELECT, UNO_DISPATCH_DF_CARD
from ..state.state_kind import StateKind
from ..state.ctl_state import CtlState
from ..lpl_cell import LplCell

from ...log.log_inst import LogInst

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
        self._cps = CellDispatchState(cell=self._cell)
        self._log = LogInst()
        self._lpl_cell = LplCell(self._cell)

    def _get_state_menu(self) -> list:
        # key = self._key_maker.ctl_state_key
        # if not self._cell.has_custom_property(key):
        #     return []
        # state = self._cell.get_custom_property(key)
        state = self._ctl_state.get_state()
        cmd = self._cps.get_rule_dispatch_cmd()
        if not cmd:
            self._log.error("CtlPopup - _get_state_menu() No dispatch command found.")
            return []
        cmd_uno = f"{cmd}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        py_obj = self._res.resolve_string("mnuViewPyObj")  # Python Object
        array = self._res.resolve_string("mnuViewArray")  # Array
        return [
            {
                "text": "State",
                "command": "",
                "submenu": [
                    {"text": py_obj, "command": cmd_uno, "enabled": state == StateKind.ARRAY},
                    {"text": array, "command": cmd_uno, "enabled": state == StateKind.PY_OBJ},
                ],
            },
        ]

    def _get_card_menu(self) -> list:
        card_name = self._res.resolve_string("mnuViewCard")
        card_url = f"{UNO_DISPATCH_DF_CARD}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        return [{"text": card_name, "command": card_url, "enabled": True}]

    def _get_popup_menu(self) -> list:
        global UNO_DISPATCH_CODE_EDIT
        edit_name = self._res.resolve_string("mnuEditCode")  # Edit Menu
        del_name = self._res.resolve_string("mnuDeletePyCell")  # Delete Python
        sel_name = self._res.resolve_string("mnuSelCell")  # Select Cell

        cmd_enabled = self._cps.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT)
        edit_url = f"{UNO_DISPATCH_CODE_EDIT}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        del_url = f"{UNO_DISPATCH_CODE_DEL}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        sel_url = f"{UNO_DISPATCH_CELL_SELECT}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        new_menu = [
            {"text": edit_name, "command": edit_url, "enabled": cmd_enabled},
            {"text": del_name, "command": del_url, "enabled": cmd_enabled},
            {"text": "-"},
            {"text": sel_name, "command": sel_url, "enabled": True},
        ]
        if self._lpl_cell.has_array_ability:
            # if self._cell.get_custom_property(self._key_maker.cell_array_ability_key, False):
            state_menu = self._get_state_menu()
            if state_menu:
                new_menu.extend(state_menu)
        if self._lpl_cell.is_dataframe:
            new_menu.extend(self._get_card_menu())
        return new_menu

    def get_menu(self) -> PopupMenu:
        creator = PopupCreator()
        pm = creator.create(self._get_popup_menu())
        # pm.add_event_item_selected(on_menu_select)
        pm.subscribe_all_item_selected(on_menu_select)
        return pm
