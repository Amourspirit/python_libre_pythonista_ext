from __future__ import annotations
import queue
import time
from typing import Any, List, cast, Dict, TYPE_CHECKING
import struct
import subprocess
import threading
import os
from pathlib import Path
import json

from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.args.event_args import EventArgs
from ooodev.events.lo_events import LoEvents
from ooodev.globals import GblEvents
from ooodev.globals import GTC
from ooodev.theme.theme_calc import ThemeCalc
from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.___lo_pip___.oxt_logger.logger_config import LoggerConfig
    from oxt.___lo_pip___.config import Config
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_code_edit import CellCodeEdit
    from oxt.pythonpath.libre_pythonista_lib.const import DISPATCH_SEL_RNG
    from oxt.pythonpath.libre_pythonista_lib.multi_process.process_mgr import ProcessMgr
    from oxt.pythonpath.libre_pythonista_lib.multi_process.socket_manager import SocketManager
    from oxt.pythonpath.libre_pythonista_lib.res.res_resolver import ResResolver
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code import py_module
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING
    from oxt.pythonpath.libre_pythonista_lib.config.dialog.wv_code_cfg import WvCodeCfg
    from oxt.pythonpath.libre_pythonista_lib.py_pip.pkg_info import PkgInfo
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.menus import menu_util as mu
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger  # noqa: F401
    from ___lo_pip___.oxt_logger.logger_config import LoggerConfig  # noqa: F401
    from ___lo_pip___.config import Config  # noqa: F401
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_code_edit import CellCodeEdit
    from libre_pythonista_lib.const import DISPATCH_SEL_RNG
    from libre_pythonista_lib.multi_process.process_mgr import ProcessMgr
    from libre_pythonista_lib.multi_process.socket_manager import SocketManager
    from libre_pythonista_lib.res.res_resolver import ResResolver
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code import py_module
    from libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING
    from libre_pythonista_lib.config.dialog.wv_code_cfg import WvCodeCfg
    from libre_pythonista_lib.py_pip.pkg_info import PkgInfo
    from libre_pythonista_lib.doc.calc.doc.menus import menu_util as mu


if os.name == "nt":
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None

_MANAGERS: Dict[str, PyCellEditProcessMgr] = {}


class PyCellCodeEdit(CellCodeEdit):
    def __init__(self, inst_id: str, cell: CalcCell, url_str: str = "", src_code: str = "") -> None:
        super().__init__(inst_id, cell, url_str, src_code)
        self._qry_handler = QryHandlerFactory.get_qry_handler()

    def _qry_pyc_instance(self) -> PySourceManager:
        qry = QryPySrcMgr(doc=self.cell.calc_doc)
        return self._qry_handler.handle(qry)

    @override
    def edit_code(self) -> bool:
        try:
            self.log.debug("Editing code for cell: %s", self.cell)
            py_inst = self._qry_pyc_instance()
            py_inst.update_source(code=self.src_code, cell_obj=self.cell.cell_obj)
            py_inst.update_all()
            return True
        except Exception:
            self.log.exception("Error editing code for cell: %s", self.cell.cell_obj)
            return False


class PyCellEditProcessMgr(ProcessMgr):
    """
    Manages subprocesses, including their creation, communication, and termination.
    This class is implemented as a singleton.
    """

    @override
    def __init__(self, *, socket_manager: SocketManager, sheet: str, cell: str) -> None:
        """
        Initializes the Editor instance.

        Args:
            socket_manager (SocketManager): Manager for handling socket connections.
            sheet (str): The name of the sheet to edit.
            cell (str): The name of the cell to edit.

        Attributes:
            log (OxtLogger): Logger instance for logging purposes.
            socket_manager (SocketManager): Manager for handling socket connections.
            process_pool (Dict[str, Tuple[subprocess.Popen, str, str]]): Dictionary to manage subprocesses.
            lock (threading.Lock): Lock for thread-safe operations.
            _term_events (TerminateEvents): Instance to handle termination events.
        """
        super().__init__(socket_manager)
        self.sheet = sheet
        self.cell = cell
        self.doc = CalcDoc.from_current_doc()
        self.cache_key = f"doc_{self.doc.runtime_uid}_sheet_{self.sheet}_cell_{self.cell}"
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._py_instance = None
        self.log.debug("Sheet: %s, Cell: %s", self.sheet, self.cell)
        calc_sheet = self.doc.sheets[sheet]
        self.calc_cell = calc_sheet[cell]
        self._res = ResResolver()
        self._gbl_cache = GTC()
        self._calc_theme = ThemeCalc()
        self._fn_on_menu_insert_lp_fn = self._on_menu_insert_lp_fn
        self._fn_on_menu_range_select_result = self._on_menu_range_select_result
        self._active_process = ""
        self._pkg_info = PkgInfo()
        self._config = Config()
        self._current_client_msg: Any = None

    @override
    def get_script_path(self) -> str:
        """
        Retrieves the path to the `shell_edit.py` script.

        Returns:
            str: The path to the `shell_edit.py` script.
        """
        pkg_location = self._pkg_info.find_module_location("librepythonista_py_edit")
        if pkg_location:
            self.log.debug("Package Location: %s", pkg_location)
            return str(Path(f"{pkg_location}") / "cell_edit.py")
        else:
            self.log.debug(
                "Package Not Found librepythonista_py_edit. Trying default.",
            )
            config = Config()
            return str(Path(config.site_packages) / "librepythonista_py_edit" / "cell_edit.py")

    @override
    def handle_client(self, process_id: str) -> None:
        """
        Handles communication with a client identified by the given process ID.
        This method continuously listens for messages from the client, processes
        them, and sends appropriate responses. It handles different types of
        messages such as 'exit', 'webview_ready', 'general_message', and 'code'.

        Args:
            process_id (str): The identifier for the client process.

        Raises:
            ConnectionResetError: If the connection is reset by the client.
            struct.error: If there is an error unpacking the message length.
            Exception: For any other exceptions that occur during message handling.

        The method ensures that the socket is closed properly in the 'finally' block.
        """
        self._active_process = process_id
        last_cmd = ""

        def update_window_config(window_config: Dict[str, Any]) -> None:
            if window_config:
                try:
                    self.log.debug("Updating window configuration")
                    wv_cfg = WvCodeCfg()
                    wv_cfg.from_dict(window_config)
                    wv_cfg.save()
                except Exception:
                    self.log.debug("Error updating window configuration. LibreOffice Window may be closed.")
            else:
                self.log.debug("No window configuration received")

        try:
            while True:
                raw_msg_len = self.socket_manager.receive_all(length=4, process_id=process_id)
                if not raw_msg_len:
                    break
                msg_len = struct.unpack("!I", raw_msg_len)[0]
                byte_data = self.socket_manager.receive_all(length=msg_len, process_id=process_id)
                if not byte_data:
                    self.log.debug("No data received")
                    break
                message = byte_data.decode(encoding="utf-8")
                json_dict = cast(Dict[str, Any], json.loads(message))
                msg_cmd = json_dict.get("cmd")
                last_cmd = msg_cmd

                if msg_cmd == "exit":
                    self.log.debug("Received exit command.")
                    # self.socket_manager.close_socket(process_id)
                    data = json_dict.get("data", {})
                    window_config = data.get("window_config", {})
                    update_window_config(window_config)
                    break
                if msg_cmd == "destroyed":
                    self.log.debug("Received destroyed command.")
                    data: Dict[str, Any] = json_dict.get("data", {})
                    # self.log.debug(f"Data: {data}")
                    window_config: Dict[str, Any] = data.get("window_config", {})
                    update_window_config(window_config)
                    logs: Dict[str, str] = data.get("logs", {})
                    if self.log.is_debug:
                        stdout = cast(List[str], logs.get("stdout", []))
                        if stdout:
                            for line in stdout:
                                self.log.debug("stdout: %s", line)
                        else:
                            self.log.debug("No stdout logs")
                    stderr = cast(List[str], logs.get("stderr", []))
                    if stderr:
                        for line in stderr:
                            self.log.error("stderr: %s", line)
                    else:
                        self.log.debug("No stderr logs")
                    break
                elif msg_cmd == "webview_ready":
                    self.log.debug("Webview is ready, sending code")
                    # code = "html = '<h2>Hello World!</h2>'\nj_data = {'a': 1, 'b': 2}\n"
                    py_src = self.py_instance[self.calc_cell.cell_obj]
                    code = py_src.source_code
                    self.socket_manager.send_message({"cmd": "code", "data": code}, process_id)
                elif msg_cmd == "general_message":
                    gen_msg = json_dict.get("data", "")
                    self.log.debug(
                        f"Received From Client {gen_msg}"
                        if gen_msg
                        else "Received From Client: general_message with no data"
                    )
                elif msg_cmd == "code":
                    py_src = self.py_instance[self.calc_cell.cell_obj]
                    current_code = py_src.source_code

                    data = json_dict.get("data", {})
                    code = data.get("code", "")
                    if code == current_code:
                        self.log.debug("Code is the same. No update required.")
                        continue
                    self.log.debug("Received code from client" if code else "Received code from client with no data")
                    inst = PyCellCodeEdit(inst_id=process_id, cell=self.calc_cell, src_code=code)
                    inst.update_cell()
                    inst = None
                    self.log.debug("Code updated")

                    window_config = data.get("window_config", {})
                    update_window_config(window_config)

                elif msg_cmd == "request_action":
                    action = cast(str, json_dict.get("action", ""))
                    params = json_dict.get("params", {})
                    self.log.debug(f"Received request for action '{action}' with params: {params}")
                    # Perform the requested action
                    result = self.perform_action(action, params)
                    msg = result.get("message", "")
                    if msg == "pass":
                        self.log.debug(f"Action '{action}' passed")
                    else:
                        # Send the result back to the client
                        self.socket_manager.send_message(
                            {"cmd": "action_completed", "response_data": result},
                            process_id,
                        )
                elif msg_cmd == "logs":
                    self.log.debug("Received logs from client")
                    log_data: Dict[str, Dict[str, str]] = json_dict.get("data", {})
                    logs: Dict[str, str] = log_data.get("logs", {})
                    if self.log.is_debug:
                        stdout = cast(List[str], logs.get("stdout", []))
                        for line in stdout:
                            self.log.debug("stdout: %s", line)
                    stderr = cast(List[str], logs.get("stderr", []))
                    for line in stderr:
                        self.log.error("stderr: %s", line)
                else:
                    self.log.error(f"Unknown message ID: {msg_cmd}")

        except (ConnectionResetError, struct.error):
            pass
        except Exception as e:
            self.log.exception(f"Error handling client: {e}")

        if last_cmd == "exit":
            PyCellEditProcessMgr.terminate_instance(self.cache_key)
        # finally:
        #     self.socket_manager.close_socket(process_id)

    def perform_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs the requested action and returns the result.

        Args:
            action (str): The action to be performed.
            params (Dict[str, Any]): The parameters for the action.

        Returns:
            Any: The result of the action.
        """

        if action == "get_info":

            def get_log_config() -> Dict[str, str]:
                log_config = LoggerConfig()
                info = log_config.to_dict()
                if self._config.is_flatpak:
                    self.log.debug("get_log_config() Flatpak detected")
                    p = Path.home() / ".librepythonista_tmp" / f"{self._config.lo_implementation_name}.log"
                    if not p.parent.exists():
                        p.parent.mkdir()
                    self.log.debug("Log File: %s", p)
                    info["log_file"] = str(p)
                else:
                    self.log.debug("get_log_config() Not Flatpak")
                return info

            # Get the resources for the given parameters
            key = "lp_editor_resources"
            if not self._gbl_cache[key]:
                self._gbl_cache[key] = {
                    "mnuAutoLpFn": self._res.resolve_string("mnuAutoLpFn").replace("~", "", 1),
                    "mnuSelectRng": self._res.resolve_string("mnuSelectRng").replace("~", "", 1),
                    "mnuValidate": self._res.resolve_string("mnuValidate").replace("~", "", 1),
                    "mnuCode": self._res.resolve_string("mnuCode").replace("~", "", 1),
                    "mnuInsert": self._res.resolve_string("mnuInsert").replace("~", "", 1),
                    "mbtitle001": self._res.resolve_string("mbtitle001"),
                    "mbmsg001": self._res.resolve_string("mbmsg001"),
                    "log09": self._res.resolve_string("log09"),
                    "title10": self._res.resolve_string("title10"),  # Python Code
                }
            self.log.debug("Getting info")
            wv_config = WvCodeCfg()
            return {
                "status": "success",
                "message": "got_info",
                "data": {
                    "info": {
                        "cell": self.cell,
                        "sheet": self.sheet,
                        "runtime_uid": self.doc.runtime_uid,
                        "is_flatpak": self._config.is_flatpak,
                        "is_snap": self._config.is_snap,
                        "is_app_image": self._config.is_app_image,
                        "python_path": str(self._config.python_path),
                        "extension_version": self._config.extension_version,
                        "extension_display_name": self._config.extension_display_name,
                    },
                    "log_config": get_log_config(),
                    "resources": cast(Dict[str, str], self._gbl_cache[key]),
                    "theme": {"is_doc_dark": self._calc_theme.is_document_dark()},
                    "window_config": wv_config.to_dict(),
                    "module_source_code": self._get_source_code(),
                },
            }
        elif action == "validate_code":
            code = params.get("code", "")
            code_valid = False
            try:
                if code:
                    self.doc.python_script.test_compile_python(code)
                code_valid = True
            except Exception:
                code_valid = False
            if code_valid:
                return {"status": "success", "message": "validated_code"}
            return {"status": "error", "message": "validated_code"}
        elif action == "insert_lp_function":
            # It is important to set the current client message to None and then monitor the value in a thread.
            # If not monitored in a thread and _on_menu_insert_lp_fn called self.socket_manager.send_message instead,
            # the message will be sent to the client but the client will not be able to send and receive any other messages.
            # This issue is likely because _on_menu_insert_lp_fn is called from a different thread.
            # By monitoring the value in a thread, the result is returned on the same thread and the client can continue to send and receive messages.
            self._current_client_msg = None
            self._write_auto_fn_sel()

            def monitor_client_msg(result_queue: queue.Queue) -> None:
                timeout = 30
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self._current_client_msg:
                        if self._current_client_msg == "aborted":
                            result_queue.put(
                                {
                                    "status": "error",
                                    "message": "pass",
                                    "data": "aborted",
                                }
                            )
                            return
                        result_queue.put(self._current_client_msg)
                        return
                    time.sleep(0.1)
                result_queue.put({"status": "error", "message": "pass", "data": "timeout"})

            # Create a queue to store the result
            result_queue = queue.Queue()
            # Start the monitor_client_msg function in a separate thread
            monitor_thread = threading.Thread(target=monitor_client_msg, args=(result_queue,), daemon=True)
            monitor_thread.start()

            # Wait for the thread to complete
            monitor_thread.join()

            # Retrieve the result from the queue
            result = result_queue.get()
            self.log.debug(f"Monitor client message result: {result}")

            return result
        elif action == "insert_range":
            # It is important to set the current client message to None and then monitor the value in a thread.
            # If not monitored in a thread and _on_menu_insert_lp_fn called self.socket_manager.send_message instead,
            # the message will be sent to the client but the client will not be able to send and receive any other messages.
            # This issue is likely because _on_menu_insert_lp_fn is called from a different thread.
            # By monitoring the value in a thread, the result is returned on the same thread and the client can continue to send and receive messages.
            self._current_client_msg = None
            self._write_range_sel()

            def monitor_client_msg(result_queue: queue.Queue) -> None:
                timeout = 30
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self._current_client_msg:
                        if self._current_client_msg == "aborted":
                            result_queue.put(
                                {
                                    "status": "error",
                                    "message": "pass",
                                    "data": "aborted",
                                }
                            )
                            return
                        result_queue.put(self._current_client_msg)
                        return
                    time.sleep(0.1)
                result_queue.put({"status": "error", "message": "pass", "data": "timeout"})

            # Create a queue to store the result
            result_queue = queue.Queue()
            # Start the monitor_client_msg function in a separate thread
            monitor_thread = threading.Thread(target=monitor_client_msg, args=(result_queue,), daemon=True)
            monitor_thread.start()

            # Wait for the thread to complete
            monitor_thread.join()

            # Retrieve the result from the queue
            result = result_queue.get()
            self.log.debug("Monitor client message result: %s", result)

            return result

        else:
            return {"status": "error", "message": f"Unknown action '{action}'"}

    # region Source Code
    def _get_source_code(self) -> str:
        try:
            init_src = py_module.get_module_init_code()
            mod_src = self.py_instance.get_module_source_code(max_cell=self.calc_cell.cell_obj, include_max=False)
            return f"{init_src}\n{mod_src}"
        except Exception:
            self.log.exception("Error getting source code")
            return ""

    # endregion Source Code

    # region Auto Function Selection
    def _on_menu_insert_lp_fn(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        # do not call self.socket_manager.send_message here. It will cause the client to break the socket because this method is called on a different thread.
        from ....data.auto_fn import AutoFn

        log = self.log
        try:
            glbs = GblEvents()
            glbs.unsubscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_insert_lp_fn)
        except Exception:
            log.error(
                "_on_menu_insert_lp_fn() unsubscribing from GlobalCalcRangeSelector",
                exc_info=True,
            )
        if event.event_data.state != "done":
            self._current_client_msg = "aborted"
            log.debug("on_sel _on_menu_insert_lp_fn aborted")
            return
        log.debug(f"_on_menu_insert_lp_fn {event.event_data.rng_obj}")
        try:
            doc = self.doc
            ro = cast(RangeObj, event.event_data.rng_obj.copy())
            sheet = doc.sheets[ro.sheet_idx]
            calc_cell_rng = sheet.get_range(range_obj=ro)
            af = AutoFn(
                cell_rng=calc_cell_rng,
                orig_sheet_idx=self.calc_cell.cell_obj.sheet_idx,
            )
            fn_str = af.generate_fn()
            if not fn_str:
                self.log.error("_on_menu_insert_lp_fn() Error generating function string")
                self._current_client_msg = "aborted"
                return

            self._current_client_msg = {
                "status": "success",
                "message": "lp_fn_inserted",
                "data": {"function": fn_str},
            }

            return
        except Exception:
            log.error("_on_menu_insert_lp_fn", exc_info=True)

    def _write_auto_fn_sel(self) -> None:
        self.log.debug("_write_auto_fn_sel() Write Range Selection Popup")
        try:
            self.doc.activate()

            # _ = TopListenerRng(self.doc)
            glbs = GblEvents()
            glbs.subscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_insert_lp_fn)
            mu.dispatch_cs_cmd(
                DISPATCH_SEL_RNG, in_thread=False, url=mu.get_url_from_command(DISPATCH_SEL_RNG), log=self.log
            )

            # self.doc.dispatch_cmd(DISPATCH_SEL_RNG)
            self.log.debug(f"Command Dispatched: {DISPATCH_SEL_RNG}")

        except Exception:
            self.log.exception("_write_auto_fn_sel() Error getting range selection")

    # endregion Auto Function Selection

    # region Range Selection
    def _on_menu_range_select_result(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        with self.log.indent(True):
            log = self.log
            try:
                glbs = GblEvents()
                glbs.unsubscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_range_select_result)
            except Exception:
                log.error(
                    "_on_menu_range_select_result() unsubscribing from GlobalCalcRangeSelector",
                    exc_info=True,
                )
            if event.event_data.state != "done":
                log.debug("on_sel _on_menu_range_select_result aborted")
                return
            log.debug(f"_on_menu_range_select_result {event.event_data.rng_obj}")
            try:
                try:
                    range_obj = cast(RangeObj, event.event_data.rng_obj.copy())

                    self.log.debug(f"_on_menu_range_select_result() Range Selection: {range_obj.to_string(True)}")

                    if range_obj.sheet_idx == self.calc_cell.cell_obj.sheet_idx:
                        if range_obj.is_single_cell():
                            self._current_client_msg = {
                                "status": "success",
                                "message": "lp_rng_inserted",
                                "data": {"range": str(range_obj.cell_start)},
                            }
                        else:
                            self._current_client_msg = {
                                "status": "success",
                                "message": "lp_rng_inserted",
                                "data": {"range": str(range_obj)},
                            }
                    else:
                        if range_obj.is_single_cell():
                            self._current_client_msg = {
                                "status": "success",
                                "message": "lp_rng_inserted",
                                "data": {"range": range_obj.cell_start.to_string(True)},
                            }
                        else:
                            self._current_client_msg = {
                                "status": "success",
                                "message": "lp_rng_inserted",
                                "data": {"range": range_obj.to_string(True)},
                            }
                except Exception:
                    log.exception("Error writing range selection using default.")
                    self._current_client_msg = "aborted"

            except Exception:
                log.error("_on_menu_range_select_result", exc_info=True)

    def _write_range_sel(self) -> None:
        self.log.debug("_write_range_sel_popup() Write Range Selection Popup")
        try:
            glbs = GblEvents()
            glbs.subscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_range_select_result)
            mu.dispatch_cs_cmd(
                DISPATCH_SEL_RNG, in_thread=False, url=mu.get_url_from_command(DISPATCH_SEL_RNG), log=self.log
            )
            # self.doc.dispatch_cmd(DISPATCH_SEL_RNG)
            self.log.debug(f"Command Dispatched: {DISPATCH_SEL_RNG}")
            # sheet.set_active()
        except Exception:
            self.log.exception("_write_range_sel_popup() Error getting range selection")

    # endregion Range Selection

    # region Static methods

    @classmethod
    def terminate_instance(cls, key: Any) -> None:  # noqa: ANN401
        global _MANAGERS
        if key in _MANAGERS:
            inst = _MANAGERS[key]
            inst.terminate_all_subprocesses()
            inst.terminate_server()
            del _MANAGERS[key]

    # endregion Static methods

    # region Properties
    @property
    def py_instance(self) -> PySourceManager:
        if self._py_instance is None:
            qry = QryPySrcMgr(doc=self.doc)
            self._py_instance = self._qry_handler.handle(qry)
        return self._py_instance

    # endregion Properties


def main(sheet: str, cell: str) -> None:
    """
    Main function to initialize and manage subprocesses.
    This function performs the following steps:

    1. Initializes the logging system with a logger named "shell_edit".
    2. Creates a SocketManager instance for managing socket connections.
    3. Creates a ProcessManager instance for managing subprocesses.
    4. Starts a subprocess using the ProcessManager.
    5. Logs the subprocess ID if the subprocess starts successfully.
    6. Logs an error message if the subprocess fails to start.

    Args:
        sheet (str): The name of the sheet to edit.
        cell (str): The name of the cell to edit

    Returns:
        None: This function does not return anything.
    """
    global _MANAGERS
    log = OxtLogger(log_name="shell_edit")
    socket_manager = SocketManager()
    process_manager = PyCellEditProcessMgr(socket_manager=socket_manager, sheet=sheet, cell=cell)
    _MANAGERS[process_manager.cache_key] = process_manager

    subprocess_id = process_manager.start_subprocess()
    if subprocess_id:
        log.debug(f"Subprocess ID: {subprocess_id}")
    else:
        log.error("Failed to start subprocess")


def _on_doc_closing(src: Any, event: EventArgs) -> None:  # noqa: ANN401
    # clean up singleton
    global _MANAGERS
    uid = str(event.event_data.uid)
    key = f"doc_{uid}"
    remove_keys = []
    for inst in _MANAGERS.values():
        if inst.cache_key.startswith(key):
            remove_keys.append(inst.cache_key)

    for remove_key in remove_keys:
        PyCellEditProcessMgr.terminate_instance(remove_key)

    for remove_key in remove_keys:
        if remove_key in _MANAGERS:
            del _MANAGERS[remove_key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
