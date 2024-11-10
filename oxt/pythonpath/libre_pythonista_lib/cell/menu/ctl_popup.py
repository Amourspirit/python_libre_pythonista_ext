from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
import threading
from urllib.parse import parse_qs, urlparse

from com.sun.star.uno import XInterface
from ooo.dyn.beans.named_value import NamedValue

from ooodev.loader import Lo
from ooodev.calc import CalcCell
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator

from ...res.res_resolver import ResResolver
from ...dispatch.cell_dispatch_state import CellDispatchState
from ..props.key_maker import KeyMaker
from ...const import (
    UNO_DISPATCH_CODE_EDIT,
    UNO_DISPATCH_CODE_EDIT_MB,
    UNO_DISPATCH_CODE_DEL,
    UNO_DISPATCH_CELL_SELECT,
    UNO_DISPATCH_CELL_SELECT_RECALC,
    UNO_DISPATCH_DF_CARD,
    UNO_DISPATCH_DATA_TBL_CARD,
    UNO_DISPATCH_CELL_CTl_UPDATE,
)
from ..state.state_kind import StateKind
from ..state.ctl_state import CtlState
from ..lpl_cell import LplCell
from ...log.log_inst import LogInst
from ...dialog.webview.lp_py_editor.job_listener import JobListener

if TYPE_CHECKING:
    from com.sun.star.awt import MenuEvent
    from ooodev.events.args.event_args import EventArgs
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


def on_menu_select(src: Any, event: EventArgs, menu: PopupMenu) -> None:
    # print("Menu Selected")
    log = LogInst()
    log.debug("on_menu_select() Menu Selected")
    log.debug(f"on_menu_select() Is Main Thread: {is_main_thread()}")
    try:
        me = cast("MenuEvent", event.event_data)
        command = menu.get_command(me.MenuId)
        if command:
            if command.startswith(".uno:service:"):
                command = command.replace(".uno:", "", 1)
            if command == "service:___lo_identifier___.AsyncJobHtmlPyEditor":
                editor_service_async(command)
                return
            if command.startswith("service:___lo_identifier___.py_edit_cell_job"):
                editor_service(command)
                return

            log.debug(f"on_menu_select() Command: {command}")
            # check if command is a dispatch command
            # is is very important that UNO_DISPATCH_CODE_EDIT_MB be executed in a thread or it wil block GUI

            if menu.is_dispatch_cmd(command):
                log.debug("on_menu_select() Dispatch Command")
                if "?" in command:
                    command_main = command.split("?")[0]
                    if command_main in (
                        UNO_DISPATCH_DF_CARD,
                        UNO_DISPATCH_CODE_EDIT,
                        UNO_DISPATCH_CODE_EDIT_MB,
                        UNO_DISPATCH_DATA_TBL_CARD,
                    ):
                        menu.execute_cmd(command, in_thread=True)
                        return

                menu.execute_cmd(command, in_thread=False)
            else:
                log.debug("on_menu_select() Not a Dispatch Command")
        else:
            log.debug("on_menu_select() Command not found.")
    except Exception:
        log.exception("on_menu_select() Error")


def is_main_thread():
    return threading.current_thread() == threading.main_thread()


def editor_service_async(service: str) -> None:
    # service = service.removeprefix("service:") # python 3.9
    service = service.replace("service:", "", 1)
    # https://wiki.documentfoundation.org/Documentation/DevGuide/Writing_UNO_Components#Initialization

    listener = JobListener(ctx=Lo.get_context())
    nv_env = NamedValue("Environment", (NamedValue("EnvType", "DISPATCH"),))

    serv = cast(Any, Lo.create_instance_mcf(XInterface, service))
    serv.executeAsync((nv_env,), listener)


def editor_service(service: str) -> None:
    # service = service.removeprefix("service:") # python 3.9
    service = service.replace("service:", "", 1)
    service_name = service.split("?")[0]
    params = get_query_params(service)
    name_values = []
    if params:
        for name, value in params.items():
            name_values.append(NamedValue(name, value))
    serv = cast(Any, Lo.create_instance_mcf(XInterface, service_name))
    if name_values:
        serv.execute(tuple(name_values))
    else:
        serv.execute(())  # are a tuple of NamedValue


def convert_query_to_dict(query: str) -> Dict[str, str]:
    if not query:
        return {}
    query_dict = parse_qs(query)
    return {k: v[0] for k, v in query_dict.items()}


def get_query_params(url_str: str) -> Dict[str, str]:
    # Parse the URL and extract the query part
    query = urlparse(url_str).query
    # Parse the query string into a dictionary
    return convert_query_to_dict(query)


class CtlPopup:
    def __init__(self, cell: CalcCell) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("Init")
        self._cell = cell
        self._res = ResResolver()
        self._config = Config()
        self._sheet_name = self._cell.calc_sheet.name
        self._key_maker = KeyMaker()
        self._ctl_state = CtlState(self._cell)
        self._cps = CellDispatchState(cell=self._cell)
        self._lpl_cell = LplCell(self._cell)

    def _get_state_menu(self) -> list:
        # key = self._key_maker.ctl_state_key
        # if not self._cell.has_custom_property(key):
        #     return []
        # state = self._cell.get_custom_property(key)
        with self._log.indent(True):
            state = self._ctl_state.get_state()
            cmd = self._cps.get_rule_dispatch_cmd()
            if not cmd:
                self._log.error(
                    "CtlPopup - _get_state_menu() No dispatch command found."
                )
                return []
            cmd_uno = f"{cmd}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
            py_obj = self._res.resolve_string("mnuViewPyObj")  # Python Object
            array = self._res.resolve_string("mnuViewArray")  # Array
            return [
                {"text": "-"},
                {
                    "text": "State",
                    "command": "",
                    "submenu": [
                        {
                            "text": py_obj,
                            "command": cmd_uno,
                            "enabled": state == StateKind.ARRAY,
                        },
                        {
                            "text": array,
                            "command": cmd_uno,
                            "enabled": state == StateKind.PY_OBJ,
                        },
                    ],
                },
            ]

    def _get_refresh_menu(self) -> list:
        refresh_ctl = self._res.resolve_string("mnuRefreshCtl")
        refresh_url = f"{UNO_DISPATCH_CELL_CTl_UPDATE}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        return [
            {"text": refresh_ctl, "command": refresh_url, "enabled": True},
        ]

    def _get_card_df_menu(self) -> list:
        card_name = self._res.resolve_string("mnuViewCard")
        card_url = f"{UNO_DISPATCH_DF_CARD}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        return [
            {"text": "-"},
            {"text": card_name, "command": card_url, "enabled": True},
        ]

    def _get_card_tbl_data_menu(self) -> list:
        card_name = self._res.resolve_string("mnuViewCard")
        card_url = f"{UNO_DISPATCH_DATA_TBL_CARD}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        return [
            {"text": "-"},
            {"text": card_name, "command": card_url, "enabled": True},
        ]

    def _get_popup_menu(self) -> list:
        edit_name = self._res.resolve_string("mnuEditCode")  # Edit Menu
        del_name = self._res.resolve_string("mnuDeletePyCell")  # Delete Python
        sel_name = self._res.resolve_string("mnuSelCell")  # Select Cell
        recalc_name = self._res.resolve_string("mnuRecalcCell")  # Recalculate

        cmd_enabled = self._cps.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT)
        self._log.debug(f"_get_popup_menu() Edit Command Enabled: {cmd_enabled}")
        if self._config.lp_settings.experimental_editor:
            # edit_url = f"{PY_EDITOR_SHEET}?py_edit_sheet&sheet={self._sheet_name}&cell={self._cell.cell_obj}"
            # edit_url = "service:___lo_identifier___.AsyncJobHtmlPyEditor"
            edit_url = f"service:___lo_identifier___.py_edit_cell_job?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        else:
            edit_url = f"{UNO_DISPATCH_CODE_EDIT_MB}?sheet={self._sheet_name}&cell={self._cell.cell_obj}&in_thread=1"
        del_url = f"{UNO_DISPATCH_CODE_DEL}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        sel_url = f"{UNO_DISPATCH_CELL_SELECT}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        sel_recalc_url = f"{UNO_DISPATCH_CELL_SELECT_RECALC}?sheet={self._sheet_name}&cell={self._cell.cell_obj}"
        new_menu = [
            {"text": edit_name, "command": edit_url, "enabled": cmd_enabled},
            {"text": del_name, "command": del_url, "enabled": cmd_enabled},
            {"text": "-"},
            {"text": sel_name, "command": sel_url, "enabled": True},
            {"text": recalc_name, "command": sel_recalc_url, "enabled": True},
        ]
        if self._lpl_cell.get_control_supports_feature("update_ctl"):
            new_menu.extend(self._get_refresh_menu())
        if not self._cps.is_protected() and self._lpl_cell.has_array_ability:
            # if self._cell.get_custom_property(self._key_maker.cell_array_ability_key, False):
            state_menu = self._get_state_menu()
            if state_menu:
                new_menu.extend(state_menu)
        if self._lpl_cell.is_dataframe:
            new_menu.extend(self._get_card_df_menu())
        if self._lpl_cell.is_table_data:
            new_menu.extend(self._get_card_tbl_data_menu())
        return new_menu

    def get_menu(self) -> PopupMenu:
        try:
            creator = PopupCreator()
            pm = creator.create(self._get_popup_menu())
            # pm.add_event_item_selected(on_menu_select)
            pm.subscribe_all_item_selected(on_menu_select)
            return pm
        except Exception:
            self._log.exception("get_menu() Error")
            raise
