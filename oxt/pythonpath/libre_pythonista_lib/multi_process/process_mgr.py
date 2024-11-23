from __future__ import annotations
from typing import Any, Dict, Tuple, Optional, TYPE_CHECKING
import socket
import threading
import subprocess
import os
import sys
import contextlib
from uuid import uuid4
from abc import ABC, abstractmethod
from pathlib import Path

from ooodev.adapter.frame.terminate_events import TerminateEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.loader import Lo


if TYPE_CHECKING:
    from .socket_manager import SocketManager
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config

if os.name == "nt":
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None


class ProcessMgr(ABC):
    """
    Abstract Class that manages subprocesses, including their creation, communication, and termination.

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
        self._server = None
        self._read_output_thread = False

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

    @abstractmethod
    def get_script_path(self) -> str:
        """
        Retrieves the path to the `shell_edit.py` script.

        Returns:
            str: The path to the python script.
        """
        ...

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
            entry_point = self.get_script_path()

            current_pythonpath = env.get("PYTHONPATH", "")
            # if config.is_flatpak:
            #     additional_paths = os.pathsep.join(
            #         [
            #             str(
            #                 Path.home()
            #                 / ".var/app/org.libreoffice.LibreOffice/sandbox/lib/python3.12/site-packages"
            #             ),
            #             os.pathsep.join(sys.path),
            #         ]
            #     )
            #     env["PYTHONPATH"] = (
            #         f"{additional_paths}{os.pathsep}{current_pythonpath}"
            #         if current_pythonpath
            #         else additional_paths
            #     )
            # else:
            additional_paths = os.pathsep.join(sys.path)

            env["PYTHONPATH"] = (
                f"{current_pythonpath}{os.pathsep}{additional_paths}"
                if current_pythonpath
                else additional_paths
            )

            if self.log.is_debug:
                self.log.debug(f"Starting shell_edit: {entry_point}")
                self.log.debug(f"Python Path: {config.python_path}")

            if self._server is None:
                server_socket, host, port, socket_file = (
                    self.socket_manager.create_server_socket()
                )
                self._server = server_socket, host, port, socket_file
            else:
                server_socket, host, port, socket_file = self._server

            process_id = str(uuid4())

            is_dbg = "debug" if self.log.is_debug else "no_debug"

            if config.is_flatpak:
                p_args = [
                    "/usr/bin/flatpak-spawn",
                    "--host",
                    "flatpak",
                    "run",
                    # "--branch=stable",
                    # "--arch=x86_64",
                    "--command=cell_edit",
                    "com.github.amourspirit.librepythonista.PyEditor",
                    "--process-id",
                    process_id,
                    # "--host",
                    # host,
                    # "--port",
                    # str(port),
                    "--socket-path",
                    socket_file,  # may start with ~
                    "--debug",
                    is_dbg,
                ]
            else:
                p_args = [
                    str(config.python_path),
                    entry_point,
                    "--process-id",
                    process_id,
                    "--host",
                    host,
                    "--port",
                    str(port),
                    "--socket-path",
                    socket_file,  # may start with ~
                    "--debug",
                    is_dbg,
                ]
            if config.is_flatpak:
                p_args.append("--kind")
                p_args.append("flatpak")
            elif config.is_snap:
                p_args.append("--kind")
                p_args.append("snap")

            if self.log.is_debug:
                self.log.debug(f"args: {p_args}")

            process = subprocess.Popen(
                p_args,
                env=None if config.is_flatpak else env,
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
                _ = self.socket_manager.accept_client(server_socket, process_id)

                if self.log.is_debug:
                    self.log.debug(f"Client connected to subprocess {process_id}")
                    self.socket_manager.send_message(
                        {"cmd": "general_message", "data": "Hello from server!"},
                        process_id,
                    )

                threading.Thread(
                    target=self.handle_client, args=(process_id,), daemon=True
                ).start()
            except socket.timeout:
                with self.lock:
                    if process_id in self.process_pool:
                        del self.process_pool[process_id]

            if self.read_output_thread:
                threading.Thread(
                    target=self.read_output, args=(process, process_id), daemon=True
                ).start()
            return process_id
        except Exception as e:
            self.log.exception(f"Error starting subprocess: {e}")
            return ""

    @abstractmethod
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

        ...

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

        Note:
            - The ``read_output_thread`` property must be set to True to enable this method to run in a separate thread.
            - When ``read_output_thread`` is set to False, this method will not be executed.
            - ``read_output_thread`` must be set to true before starting ``start_subprocess`` is called to enable output reading.
            - ``read_output_thread`` is set to False by default.
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
                    self.log.debug(
                        "Subprocess %s removed from process pool", process_id
                    )

    def terminate_server(self):
        """
        Terminates the server socket.

        Returns:
            None: This method does not return anything.
        """

        if self._server:
            server_socket, host, port, socket_file = self._server
            self.log.debug("Terminating server socket")
            server_socket.close()
            try:
                if socket_file:
                    if socket_file.startswith("~"):
                        socket_file = os.path.expanduser(socket_file)
                    if os.path.exists(socket_file):
                        self.log.debug("Removing socket file: %s", socket_file)
                        os.remove(socket_file)
                    else:
                        self.log.debug("Socket file does not exist: %s", socket_file)
                else:
                    self.log.debug("No socket file to remove")
            except Exception as e:
                self.log.error(f"Error removing socket file: {e}")
            self._server = None

    def __del__(self):
        """
        Destructor for the ProcessMgr class.
        This method is called when the ProcessMgr instance is deleted.
        It ensures that all subprocesses are terminated before the instance is destroyed.
        """
        with contextlib.suppress(Exception):
            self.terminate_all_subprocesses()
            self.terminate_server()

    @property
    def read_output_thread(self):
        """
        Returns the thread responsible for reading output.
        This method provides access to the thread that handles the reading of output
        from a subprocess or another source. Default value is ``False``.

        Returns:
            threading.Thread: The thread responsible for reading output.
        """

        return self._read_output_thread

    @read_output_thread.setter
    def read_output_thread(self, value):
        self._read_output_thread = value
