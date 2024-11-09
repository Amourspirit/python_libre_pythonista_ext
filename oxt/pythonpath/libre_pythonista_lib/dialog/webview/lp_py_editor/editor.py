from __future__ import annotations
from typing import Any, cast, Dict, Tuple, Optional, TYPE_CHECKING
import socket
import struct
import threading
import subprocess
import os
import sys

# import atexit
from pathlib import Path
from uuid import uuid4
import json

from ooodev.adapter.frame.terminate_events import TerminateEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.loader import Lo

_TIMEOUT = 10

if TYPE_CHECKING:
    from ......___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ......___lo_pip___.config import Config
    # from ......pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    # from libre_pythonista_lib.event.shared_event import SharedEvent

# https://stackoverflow.com/search?q=%5Bpython%5D+run+subprocess+without+popup+terminal
# silent subprocess
if os.name == "nt":
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None


class SubprocessManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SubprocessManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.log = OxtLogger(log_name="shell_edit")
        self.process_pool: Dict[str, Tuple[subprocess.Popen, str, str]] = {}
        # process_pool = {process_id: (process, port, doc_id)}
        self._socket_pool: Dict[str, socket.socket] = {}
        self.lock = threading.Lock()
        # atexit.register(self.terminate_all_subprocesses)
        self._term_events = TerminateEvents()
        self._fn_on_notify_termination = self._on_notify_termination
        self._term_events.add_event_notify_termination(self._fn_on_notify_termination)
        self._initialized = True

    def _on_notify_termination(self, src: Any, event: EventArgs) -> None:
        """
        Is called when the master environment (e.g., desktop) is about to terminate.

        Termination can be intercepted by throwing TerminationVetoException.
        Interceptor will be the new owner of desktop and should call XDesktop.terminate() after finishing his own operations.

        Raises:
            TerminationVetoException: ``TerminationVetoException``
        """
        self.log.debug("on_notify_termination()")
        self.terminate_all_subprocesses()

    def start_subprocess(self) -> str:
        """Starts a new subprocess and adds it to the process pool."""
        global _TIMEOUT
        try:
            env = os.environ.copy()

            config = Config()
            root = Path(__file__).parent
            script_path = str(Path(root, "shell_edit.py"))
            # Include the current sys.path in the PYTHONPATH environment variable
            current_pythonpath = env.get("PYTHONPATH", "")
            additional_paths = os.pathsep.join(sys.path)
            if current_pythonpath:
                env["PYTHONPATH"] = (
                    f"{current_pythonpath}{os.pathsep}{additional_paths}"
                )
            else:
                env["PYTHONPATH"] = additional_paths

            if self.log.is_debug:
                self.log.debug(f"Starting shell_edit: {script_path}")
                self.log.debug(f"Python Path: {config.python_path}")

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("localhost", 0))  # Bind to an available port
            host, port = server_socket.getsockname()

            server_socket.listen(1)
            server_socket.settimeout(_TIMEOUT)  # Set a timeout of 10 seconds

            process_id = str(uuid4())

            is_dbg = "debug" if self.log.is_debug else "no_debug"

            if STARTUP_INFO:
                process = subprocess.Popen(
                    [
                        str(config.python_path),
                        script_path,
                        process_id,
                        str(port),
                        is_dbg,
                    ],
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    startupinfo=STARTUP_INFO,
                )
            else:
                process = subprocess.Popen(
                    [
                        str(config.python_path),
                        script_path,
                        process_id,
                        str(port),
                        is_dbg,
                    ],
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

            with self.lock:
                self.process_pool[process_id] = (
                    process,
                    str(port),
                    Lo.current_doc.runtime_uid,
                )

            try:
                # Accept the connection from the client
                client_socket, _ = server_socket.accept()
                self._socket_pool[process_id] = client_socket
                self.log.debug(f"Client connected to subprocess {process_id}")

                # Send a message to the client
                data = {
                    "cmd": "general_message",
                    "data": "Hello from server!",
                }
                self.send_message(data, process_id)

                # Handle communication in a separate thread
                threading.Thread(
                    target=self.handle_client, args=(process_id,), daemon=True
                ).start()
            except socket.timeout:
                print(
                    f"Accept timed out. No client connected within {_TIMEOUT} seconds."
                )
                server_socket.close()
                with self.lock:
                    if process_id in self.process_pool:
                        del self.process_pool[process_id]
                # _VIEW_DONE = True

            threading.Thread(
                target=self.read_output, args=(process, process_id), daemon=True
            ).start()

            return process_id
        except Exception as e:
            self.log.exception(f"Error starting subprocess: {e}")
            return ""

    def send_message(self, message: Dict[str, Any], process_id: str) -> None:
        # Prefix each message with a 4-byte length (network byte order)
        with self.lock:
            try:
                if process_id not in self._socket_pool:
                    self.log.error(
                        f"send_message() Process {process_id} not found in socket pool"
                    )
                    return
                sock = self._socket_pool[process_id]
                json_message = json.dumps(message)
                message_bytes = json_message.encode()
                message_length = struct.pack("!I", len(message_bytes))
                self.log.debug(
                    f"Sending message to client: {message} to process {process_id}"
                )
                sock.sendall(message_length + message_bytes)
            except Exception:
                self.log.exception("Error sending message")

    def receive_all(self, length: int, process_id: str) -> bytes:
        data = b""
        with self.lock:
            if process_id not in self._socket_pool:
                return data
            sock = self._socket_pool[process_id]
        while len(data) < length:
            more = sock.recv(length - len(data))
            if not more:
                raise ConnectionResetError("Connection closed prematurely")
            data += more
        return data

    def handle_client(self, process_id: str) -> None:
        with self.lock:
            if process_id not in self._socket_pool:
                self.log.error(
                    f"handle_client() Process {process_id} not found in socket pool"
                )
                return
            sock = self._socket_pool[process_id]
        try:
            while True:
                try:
                    # Receive the message length first
                    raw_msg_len = self.receive_all(length=4, process_id=process_id)
                    if not raw_msg_len:
                        break
                    msg_len = struct.unpack("!I", raw_msg_len)[0]

                    # Receive the actual message
                    data = self.receive_all(length=msg_len, process_id=process_id)
                    if not data:
                        self.log.debug("No data received")
                        break
                    message = data.decode()
                    json_dict = cast(Dict[str, Any], json.loads(message))
                    msg_cmd = json_dict.get("cmd")
                    # self.log.debug(f"Received From Client: {message}")

                    if msg_cmd == "exit":
                        break
                    elif msg_cmd == "webview_ready":
                        self.log.debug("Webview is ready, sending code")
                        code = "html = '<h2>Hello World!</h2>'\nj_data = {'a': 1, 'b': 2}\n"
                        data = {
                            "cmd": "code",
                            "data": code,
                        }
                        self.send_message(data, process_id)
                    elif msg_cmd == "general_message":
                        gen_msg = json_dict.get("data", "")
                        if gen_msg:
                            self.log.debug(f"Received From Client {gen_msg}")
                        else:
                            self.log.debug(
                                "Received From Client: general_message with no data"
                            )
                    elif msg_cmd == "code":
                        code = json_dict.get("data", "")
                        if code:
                            self.log.debug("Received code from client")
                        else:
                            self.log.debug("Received code from client with no data")
                    else:
                        self.log.error(f"Unknown message ID: {msg_cmd}")
                except (ConnectionResetError, struct.error):
                    break
            sock.close()
        except Exception as e:
            self.log.exception(f"Error handling client: {e}")
        finally:
            if process_id in self._socket_pool:
                del self._socket_pool[process_id]

    def terminate_subprocess(self, process_id: str):
        """Terminates the specified subprocess."""
        process = self.get_process(process_id)
        if not process:
            self.log.error(f"Process with ID {process_id} does not exist.")
            return
        self.log.debug(f"Terminating subprocess {process_id}")
        data = {
            "cmd": "destroy",
            "data": "destroy",
        }
        self.send_message(data, process_id)
        # if process.poll() is None:
        #     self.log.info(f"Forcefully terminating subprocess {process_id}")
        #     process.terminate()
        #     try:
        #         process.wait(timeout=5)
        #     except subprocess.TimeoutExpired:
        #         self.log.warning(
        #             f"Subprocess {process_id} did not terminate in time, killing it"
        #         )
        #         process.kill()
        with self.lock:
            del self.process_pool[process_id]

    def terminate_all_subprocesses(self):
        """Terminates all subprocesses in the process pool."""
        self.log.info("Terminating all subprocesses")
        process_ids = list(self.process_pool.keys())
        for process_id in process_ids:
            self.terminate_subprocess(process_id)

    def get_process(self, process_id: str) -> Optional[subprocess.Popen]:
        """read_output() Retrieves a subprocess by its ID."""
        with self.lock:
            result = self.process_pool.get(process_id)
            if result:
                return result[0]

    def read_output(self, process: subprocess.Popen, process_id: str):
        """Reads the output of the subprocess asynchronously."""
        try:
            if process.stdout is None or process.stderr is None:
                self.log.error(
                    f"Subprocess {process_id} stdout/stderr is not available"
                )
                return
            for line in iter(process.stdout.readline, ""):
                line: str  # Variable annotation
                self.log.debug(f"Subprocess {process_id} output: {line.strip()}")
            process.stdout.close()

            for line in iter(process.stderr.readline, ""):
                line: str  # Variable annotation
                self.log.error(f"Subprocess {process_id} error: {line.strip()}")
            process.stderr.close()

            process.wait()
            self.log.debug(
                f"Subprocess {process_id} finished with return code {process.returncode}"
            )
        except Exception as e:
            self.log.exception(f"Error reading output for subprocess {process_id}: {e}")
        finally:
            with self.lock:
                if process_id in self.process_pool:
                    del self.process_pool[process_id]
                    self.log.debug(f"Subprocess {process_id} removed from process pool")

    # Additional methods can be added as needed


def main():
    manager = SubprocessManager()

    # Start a new subprocess
    subprocess_id = manager.start_subprocess()
    if subprocess_id:
        manager.log.debug(f"Subprocess ID: {subprocess_id}")

    else:
        manager.log.error("Failed to start subprocess")
