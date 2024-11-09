from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
import struct
import subprocess
import os
from pathlib import Path
import json

from ooodev.calc import CalcDoc, CalcCell
from ....multi_process.socket_manager import SocketManager
from ....multi_process.process_mgr import ProcessMgr
from ....code.py_source_mgr import PyInstance
from ....cell.code_edit.cell_code_edit import CellCodeEdit

if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    from ......___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ......___lo_pip___.config import Config
else:
    override = lambda func: func  # noqa: E731
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger  # noqa: F401
    from ___lo_pip___.config import Config  # noqa: F401

if os.name == "nt":
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None


class PyCellCodeEdit(CellCodeEdit):
    def __init__(
        self, inst_id: str, cell: CalcCell, url_str: str = "", src_code: str = ""
    ):
        CellCodeEdit.__init__(self, inst_id, cell, url_str, src_code)

    @override
    def edit_code(self) -> bool:
        try:
            self.log.debug(f"Editing code for cell: {self.cell}")
            py_inst = PyInstance(self.cell.calc_doc)  # singleton
            py_inst.update_source(code=self.src_code, cell=self.cell.cell_obj)
            py_inst.update_all()
            return True
        except Exception:
            self.log.exception(f"Error editing code for cell: {self.cell.cell_obj}")
            return False


class PyCellEditProcessMgr(ProcessMgr):
    """
    Manages subprocesses, including their creation, communication, and termination.
    """

    @override
    def __init__(self, socket_manager: SocketManager, sheet: str, cell: str):
        """
        Initializes the Editor instance.

        Args:
            socket_manager (SocketManager): Manager for handling socket connections.
            sheet (str): The name of the sheet to edit.
            cell (str): The name of the cell to edit

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
        self.py_instance = PyInstance(self.doc)
        self.log.debug(f"Sheet: {self.sheet}, Cell: {self.cell}")
        calc_sheet = self.doc.sheets[sheet]
        self.calc_cell = calc_sheet[cell]

    @override
    def get_script_path(self) -> str:
        """
        Retrieves the path to the `shell_edit.py` script.

        Returns:
            str: The path to the `shell_edit.py` script.
        """

        root = Path(__file__).parent
        return str(Path(root, "shell_edit.py"))

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

        try:
            while True:
                raw_msg_len = self.socket_manager.receive_all(
                    length=4, process_id=process_id
                )
                if not raw_msg_len:
                    break
                msg_len = struct.unpack("!I", raw_msg_len)[0]
                data = self.socket_manager.receive_all(
                    length=msg_len, process_id=process_id
                )
                if not data:
                    self.log.debug("No data received")
                    break
                message = data.decode()
                json_dict = cast(Dict[str, Any], json.loads(message))
                msg_cmd = json_dict.get("cmd")

                if msg_cmd == "exit":
                    break
                elif msg_cmd == "webview_ready":
                    self.log.debug("Webview is ready, sending code")
                    # code = "html = '<h2>Hello World!</h2>'\nj_data = {'a': 1, 'b': 2}\n"
                    py_src = self.py_instance[self.calc_cell.cell_obj]
                    code = py_src.source_code
                    self.socket_manager.send_message(
                        {"cmd": "code", "data": code}, process_id
                    )
                elif msg_cmd == "general_message":
                    gen_msg = json_dict.get("data", "")
                    self.log.debug(
                        f"Received From Client {gen_msg}"
                        if gen_msg
                        else "Received From Client: general_message with no data"
                    )
                elif msg_cmd == "code":
                    code = json_dict.get("data", "")
                    self.log.debug(
                        "Received code from client"
                        if code
                        else "Received code from client with no data"
                    )
                    inst = PyCellCodeEdit(
                        inst_id=process_id, cell=self.calc_cell, src_code=code
                    )
                    inst.update_cell()
                    inst = None
                    self.log.debug("Code updated")
                else:
                    self.log.error(f"Unknown message ID: {msg_cmd}")
        except (ConnectionResetError, struct.error):
            pass
        except Exception as e:
            self.log.exception(f"Error handling client: {e}")
        finally:
            self.socket_manager.close_socket(process_id)


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

    log = OxtLogger(log_name="shell_edit")
    socket_manager = SocketManager()
    process_manager = PyCellEditProcessMgr(
        socket_manager=socket_manager, sheet=sheet, cell=cell
    )

    subprocess_id = process_manager.start_subprocess()
    if subprocess_id:
        log.debug(f"Subprocess ID: {subprocess_id}")
    else:
        log.error("Failed to start subprocess")
