from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
import struct
import subprocess
import os
from pathlib import Path
import json


from ....multi_process.socket_manager import SocketManager
from ....multi_process.process_mgr import ProcessMgr


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


class PyCellEditProcessMgr(ProcessMgr):
    """
    Manages subprocesses, including their creation, communication, and termination.
    """

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
                    code = "html = '<h2>Hello World!</h2>'\nj_data = {'a': 1, 'b': 2}\n"
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
                else:
                    self.log.error(f"Unknown message ID: {msg_cmd}")
        except (ConnectionResetError, struct.error):
            pass
        except Exception as e:
            self.log.exception(f"Error handling client: {e}")
        finally:
            self.socket_manager.close_socket(process_id)


def main():
    """
    Main function to initialize and manage subprocesses.
    This function performs the following steps:

    1. Initializes the logging system with a logger named "shell_edit".
    2. Creates a SocketManager instance for managing socket connections.
    3. Creates a ProcessManager instance for managing subprocesses.
    4. Starts a subprocess using the ProcessManager.
    5. Logs the subprocess ID if the subprocess starts successfully.
    6. Logs an error message if the subprocess fails to start.

    Returns:
        None: This function does not return anything.
    """

    log = OxtLogger(log_name="shell_edit")
    socket_manager = SocketManager()
    process_manager = PyCellEditProcessMgr(socket_manager)

    subprocess_id = process_manager.start_subprocess()
    if subprocess_id:
        log.debug(f"Subprocess ID: {subprocess_id}")
    else:
        log.error("Failed to start subprocess")
