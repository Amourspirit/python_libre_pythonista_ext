from __future__ import annotations
from typing import Any, cast, Dict, Tuple, Optional, TYPE_CHECKING
import socket
import struct
import threading
import subprocess
import os
import sys
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
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config

if os.name == "nt":
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None


class SocketManager:
    """
    SocketManager is a class responsible for managing socket connections, including creating server sockets, accepting client connections, sending messages, receiving data, and closing sockets.
    It ensures thread safety using a lock and logs various actions and errors.

    Methods:
        __init__(log: OxtLogger):
            Initializes the SocketManager with a logger, a socket pool, and a lock.
        create_server_socket() -> Tuple[socket.socket, int]:
        accept_client(server_socket: socket.socket, process_id: str) -> socket.socket:
        send_message(message: Dict[str, Any], process_id: str) -> None:
        receive_all(length: int, process_id: str) -> bytes:
        close_socket(process_id: str) -> None:
    """

    def __init__(self):
        """
        Initializes the editor with a logger, a socket pool, and a lock.


        Attributes:
            _socket_pool (Dict[str, socket.socket]): A dictionary to store socket connections.
            log (OxtLogger): The logger instance.
            lock (threading.Lock): A lock to ensure thread safety.
        """

        self._socket_pool: Dict[str, socket.socket] = {}
        self.log = OxtLogger(log_name=self.__class__.__name__)
        self.lock = threading.Lock()

    def create_server_socket(self) -> Tuple[socket.socket, int]:
        """
        Creates a server socket bound to an available port on localhost.

        Returns:
            Tuple[socket.socket, int]: A tuple containing the server socket object and the port number it is bound to.
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", 0))  # Bind to an available port
        host, port = server_socket.getsockname()
        server_socket.listen(1)
        server_socket.settimeout(_TIMEOUT)  # Set a timeout of 10 seconds
        return server_socket, port

    def accept_client(
        self, server_socket: socket.socket, process_id: str
    ) -> socket.socket:
        """
        Accepts a client connection on the given server socket and associates it with a process ID.

        Args:
            server_socket (socket.socket): The server socket to accept the client connection on.
            process_id (str): The ID of the process to associate with the client connection.

        Returns:
            socket.socket: The client socket that was accepted.

        Raises:
            socket.timeout: If no client connects within the specified timeout period.
        """
        try:
            client_socket, _ = server_socket.accept()
            with self.lock:
                self._socket_pool[process_id] = client_socket
            self.log.debug(f"Client connected to subprocess {process_id}")
            return client_socket
        except socket.timeout:
            self.log.error(
                f"Accept timed out. No client connected within {_TIMEOUT} seconds."
            )
            server_socket.close()
            raise

    def send_message(self, message: Dict[str, Any], process_id: str) -> None:
        """
        Sends a JSON-encoded message to a client process via a socket.

        Args:
            message (Dict[str, Any]): The message to be sent, represented as a dictionary.
            process_id (str): The identifier of the client process to which the message will be sent.

        Returns:
            None: This method does not return anything.

        Raises:
            None: This method does not raise any exceptions.

        Logs:
            Logs an error if the process_id is not found in the socket pool.
            Logs the message being sent and the target process_id at debug level.
            Logs an exception if an error occurs while sending the message.
        """

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
        """
        Receives a specified number of bytes from a socket associated with a given process ID.

        Args:
            length (int): The number of bytes to receive.
            process_id (str): The ID of the process whose socket will be used to receive data.

        Returns:
            bytes: The received data.

        Raises:
            ConnectionResetError: If the connection is closed prematurely.
        """

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

    def close_socket(self, process_id: str) -> None:
        """
        Closes and removes the socket associated with the given process ID.

        Args:
            process_id (str): The ID of the process whose socket needs to be closed.
        Returns:
            None: This method does not return anything.
        """

        with self.lock:
            if process_id in self._socket_pool:
                self._socket_pool[process_id].close()
                del self._socket_pool[process_id]


class ProcessManager:
    """
    Manages subprocesses, including their creation, communication, and termination.

        Attributes:
        log (OxtLogger): Logger for logging messages.
        socket_manager (SocketManager): Manages socket communication.
        process_pool (Dict[str, Tuple[subprocess.Popen, str, str]]): Pool of active subprocesses.
        lock (threading.Lock): Lock for synchronizing access to process_pool.
        _term_events (TerminateEvents): Manages termination events.

            Methods:
        __init__(log: OxtLogger, socket_manager: SocketManager):
            Initializes the ProcessManager with a logger and socket manager.
        _on_notify_termination(src: Any, event: EventArgs) -> None:
            Handles termination notifications and terminates all subprocesses.
        start_subprocess() -> str:
            Starts a new subprocess and returns its process ID.
        handle_client(process_id: str) -> None:
            Handles communication with a client subprocess.
        terminate_subprocess(process_id: str):
            Terminates a specific subprocess by its process ID.
        terminate_all_subprocesses():
            Terminates all active subprocesses.
        get_process(process_id: str) -> Optional[subprocess.Popen]:
            Retrieves a subprocess by its process ID.
        read_output(process: subprocess.Popen, process_id: str):
            Reads and logs the output and errors from a subprocess.
    """

    def __init__(self, socket_manager: SocketManager):
        """
        Initializes the Editor instance.
        Args:
            socket_manager (SocketManager): Manager for handling socket connections.
        Attributes:
            log (OxtLogger): Logger instance for logging purposes.
            socket_manager (SocketManager): Manager for handling socket connections.
            process_pool (Dict[str, Tuple[subprocess.Popen, str, str]]): Dictionary to manage subprocesses.
            lock (threading.Lock): Lock for thread-safe operations.
            _term_events (TerminateEvents): Instance to handle termination events.
        """

        self.log = OxtLogger(log_name=self.__class__.__name__)
        self.socket_manager = socket_manager
        self.process_pool: Dict[str, Tuple[subprocess.Popen, str, str]] = {}
        self.lock = threading.Lock()
        self._term_events = TerminateEvents()
        self._term_events.add_event_notify_termination(self._on_notify_termination)

    def _on_notify_termination(self, src: Any, event: EventArgs) -> None:
        """
        Handles the notification of termination events.
        This method is called when a termination event is received. It logs the
        termination event and then proceeds to terminate all subprocesses.

        Args:
            src (Any): The source of the event.
            event (EventArgs): The event arguments containing details about the termination event.

        Returns:
            None: This method does not return anything.
        """

        self.log.debug("on_notify_termination()")
        self.terminate_all_subprocesses()

    def start_subprocess(self) -> str:
        """
        Starts a subprocess to run a specified script with a unique process ID and port.
        This method sets up the environment variables, creates a server socket, and starts
        a subprocess to run the `shell_edit.py` script. It also handles client connections
        and reads the output from the subprocess.

        Returns:
            str: The unique process ID of the started subprocess. Returns an empty string
                if an error occurs during the subprocess startup.

        Raises:
            Exception: If there is an error during the subprocess startup, it logs the
                exception and returns an empty string.
        """

        try:
            env = os.environ.copy()
            config = Config()
            root = Path(__file__).parent
            script_path = str(Path(root, "shell_edit.py"))
            current_pythonpath = env.get("PYTHONPATH", "")
            additional_paths = os.pathsep.join(sys.path)
            env["PYTHONPATH"] = (
                f"{current_pythonpath}{os.pathsep}{additional_paths}"
                if current_pythonpath
                else additional_paths
            )

            if self.log.is_debug:
                self.log.debug(f"Starting shell_edit: {script_path}")
                self.log.debug(f"Python Path: {config.python_path}")

            server_socket, port = self.socket_manager.create_server_socket()
            process_id = str(uuid4())
            is_dbg = "debug" if self.log.is_debug else "no_debug"

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

            with self.lock:
                self.process_pool[process_id] = (
                    process,
                    str(port),
                    Lo.current_doc.runtime_uid,
                )

            try:
                client_socket = self.socket_manager.accept_client(
                    server_socket, process_id
                )
                self.socket_manager.send_message(
                    {"cmd": "general_message", "data": "Hello from server!"}, process_id
                )
                threading.Thread(
                    target=self.handle_client, args=(process_id,), daemon=True
                ).start()
            except socket.timeout:
                with self.lock:
                    if process_id in self.process_pool:
                        del self.process_pool[process_id]

            threading.Thread(
                target=self.read_output, args=(process, process_id), daemon=True
            ).start()
            return process_id
        except Exception as e:
            self.log.exception(f"Error starting subprocess: {e}")
            return ""

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

    def terminate_subprocess(self, process_id: str):
        """
        Terminates a subprocess given its process ID.

        Args:
            process_id (str): The ID of the subprocess to terminate.

        Returns:
            None: This method does not return anything.

        Logs:
            - Error if the process with the given ID does not exist.
            - Debug information when terminating the subprocess.

        Actions:
            - Sends a "destroy" command to the subprocess via the socket manager.
            - Removes the subprocess from the process pool.
        """

        process = self.get_process(process_id)
        if not process:
            self.log.error(f"Process with ID {process_id} does not exist.")
            return
        self.log.debug(f"Terminating subprocess {process_id}")
        self.socket_manager.send_message(
            {"cmd": "destroy", "data": "destroy"}, process_id
        )
        with self.lock:
            del self.process_pool[process_id]

    def terminate_all_subprocesses(self):
        """
        Terminates all subprocesses managed by the process pool.
        This method logs the termination process and iterates through all
        subprocess IDs in the process pool, terminating each one individually.
        """

        self.log.info("Terminating all subprocesses")
        process_ids = list(self.process_pool.keys())
        for process_id in process_ids:
            self.terminate_subprocess(process_id)

    def get_process(self, process_id: str) -> Optional[subprocess.Popen]:
        """
        Retrieve a subprocess from the process pool using the given process ID.

        Args:
            process_id (str): The unique identifier for the subprocess.

        Returns:
            Optional[subprocess.Popen]: The subprocess associated with the given process ID,
                or None if no such subprocess exists.
        """

        with self.lock:
            result = self.process_pool.get(process_id)
            return result[0] if result else None

    def read_output(self, process: subprocess.Popen, process_id: str):
        """
        Reads the output and error streams of a subprocess and logs the information.

        Args:
            process (subprocess.Popen): The subprocess whose output and error streams are to be read.
            process_id (str): The identifier for the subprocess.

        Logs:
            - Debug information for each line of output from the subprocess.
            - Error information for each line of error output from the subprocess.
            - Debug information when the subprocess finishes, including its return code.
            - Exception information if an error occurs while reading the output.

        Ensures:
            - The subprocess is removed from the process pool when finished.
        """

        try:
            if process.stdout is None or process.stderr is None:
                self.log.error(
                    f"Subprocess {process_id} stdout/stderr is not available"
                )
                return
            for line in iter(process.stdout.readline, ""):
                self.log.debug(f"Subprocess {process_id} output: {line.strip()}")
            process.stdout.close()

            for line in iter(process.stderr.readline, ""):
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
    process_manager = ProcessManager(socket_manager)

    subprocess_id = process_manager.start_subprocess()
    if subprocess_id:
        log.debug(f"Subprocess ID: {subprocess_id}")
    else:
        log.error("Failed to start subprocess")
