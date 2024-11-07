from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING
import multiprocessing
import threading
import subprocess
import os
import sys
import atexit
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4
import time

from ooodev.adapter.frame.terminate_events import TerminateEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.loader import Lo

if TYPE_CHECKING:
    from ......___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ......___lo_pip___.config import Config
    # from ......pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    # from libre_pythonista_lib.event.shared_event import SharedEvent


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
        self.process_pool: Dict[str, Tuple[subprocess.Popen, Any]] = {}
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
        try:
            # Create a multiprocessing Pipe
            parent_conn, child_conn = multiprocessing.Pipe()

            # Get the file descriptor of the child connection
            child_conn_fd = child_conn.fileno()

            # Pass the file descriptor to the subprocess via environment variables
            env = os.environ.copy()

            # Duplicate the file descriptor for safety
            child_conn_fd_dup = os.dup(child_conn_fd)

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

            process = subprocess.Popen(
                [
                    str(config.python_path),
                    script_path,
                    Lo.current_doc.runtime_uid,
                    str(child_conn_fd_dup),
                ],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # stdin=subprocess.PIPE,
                text=True,
                pass_fds=(child_conn_fd_dup,),
            )

            process_id = str(uuid4())
            with self.lock:
                self.process_pool[process_id] = (process, parent_conn)

            threading.Thread(
                target=self.read_output, args=(process, process_id), daemon=True
            ).start()

            # Start a thread to read messages from the subprocess
            threading.Thread(
                target=self.read_from_subprocess,
                args=(parent_conn, process_id),
                daemon=True,
            ).start()
            return process_id
        except Exception as e:
            self.log.exception(f"Error starting subprocess: {e}")
            return ""

    def read_from_subprocess(self, conn, process_id):
        """Reads messages from the subprocess."""
        try:
            while True:
                message = conn.recv()
                self.log.debug(f"Received from subprocess {process_id}: {message}")
                if message == "webview_ready":
                    self.send_message(
                        process_id, 'set_code: html = "<h2>Hello World!</h2>"'
                    )
        except EOFError:
            print(f"Subprocess {process_id} connection closed.")

    def send_message(self, process_id: str, message: str):
        """Sends a message to the subprocess."""
        with self.lock:
            process_tuple = self.process_pool.get(process_id)
        if process_tuple:
            _, conn = process_tuple
            conn.send(message)
        else:
            print(f"No subprocess with ID {process_id} found.")

    def terminate_subprocess(self, process_id: str):
        """Terminates the specified subprocess."""
        process = self.get_process(process_id)
        if not process:
            self.log.error(f"Process with ID {process_id} does not exist.")
            return
        self.log.debug(f"Terminating subprocess {process_id}")
        self.send_message(process_id, "destroy")
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
