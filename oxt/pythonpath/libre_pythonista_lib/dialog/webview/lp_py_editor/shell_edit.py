from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING
import socket
import struct
import sys
import json
import threading
from pathlib import Path
import webview
import jedi  # noqa # type: ignore

# from ooodev.adapter.frame.terminate_events import TerminateEvents
# from ooodev.events.args.event_args import EventArgs

if TYPE_CHECKING:
    from ......pythonpath.libre_pythonista_lib.dialog.webview.lp_py_editor.menu import (
        menu_items,
    )
else:
    from libre_pythonista_lib.dialog.webview.lp_py_editor.menu import menu_items

# https://pywebview.flowrl.com/guide/api.html#webview-settings

webview.settings = {
    "ALLOW_DOWNLOADS": False,
    "ALLOW_FILE_URLS": True,
    "OPEN_EXTERNAL_LINKS_IN_BROWSER": True,
    "OPEN_DEVTOOLS_IN_DEBUG": False,
}

_WEB_VEW_ENDED = False


class Api:
    def __init__(self, doc_id: str, sock: socket.socket, port: int):
        self._window = cast(webview.Window, None)
        self._doc_id = doc_id
        self.port = port
        self.sock = sock

    def set_window(self, window: webview.Window):
        self._window = window

    def destroy(self):
        global _WEB_VEW_ENDED
        try:
            if self._window:
                # Destroy the window in a separate thread
                # self.hide()
                self._window.destroy()
                self._window = cast(webview.Window, None)
                _WEB_VEW_ENDED = True
        except Exception as e:
            sys.stderr.write(f"Error in destroy {e}\n")

    def hide(self):
        try:
            if self._window:
                if not self._window.hidden:
                    sys.stdout.write("Hiding window\n")
                    self._window.hide()
                    sys.stdout.write("Window hidden'n")
                else:
                    sys.stdout.write("Window already hidden\n")
        except Exception as e:
            sys.stderr.write(f"Error in hide {e}\n")

    def show(self):
        try:
            if self._window:
                sys.stdout.write("Showing window\n")
                self._window.show()
                sys.stdout.write("Window shown\n")
        except Exception as e:
            sys.stderr.write(f"Error in show: {e}\n")

    def accept(self) -> None:
        try:
            if self._window:
                code = self._window.evaluate_js("getCode()")
                sys.stdout.write("Code:\n{}\n".format(code))
                data = {
                    "id": "code",
                    "doc_id": self._doc_id,
                    "data": code,
                }
                send_message(self.sock, data)
                sys.stdout.write("Sent code to server\n")
                self.destroy()

        except Exception as e:
            sys.stderr.write(f"Error in accept: {e}\n")

    def log(self, value):
        try:
            code = self._window.evaluate_js("getCode()")
            sys.stdout.write("Code:\n{}\n".format(code))
        except Exception as e:
            sys.stderr.write(f"Error in log: {e}")

    def get_autocomplete(self, code, line, column):
        try:
            code = self._window.evaluate_js("getCode()")
            # print("code:\n", code)
            script = jedi.Script(code, path="")
            # print("script:\n", script)
            completions = script.complete(line, column)
            suggestions = [completion.name for completion in completions]
            # print()
            # print("Suggestions:\n", suggestions)
            return json.dumps(suggestions)
        except Exception:
            return json.dumps([])

    def has_window(self):
        return self._window is not None

    def set_code(self, code: str):
        try:
            if self._window:
                escaped_code = json.dumps(code)  # Escape the string for JavaScript
                # sys.stdout.write(f"{escaped_code}\n")
                self._window.evaluate_js(f"setCode({escaped_code})")
        except Exception as e:
            sys.stderr.write(f"Error in set_code: {e}\n")


def webview_ready(window: webview.Window):
    pass
    # code = "# Write your code here! \nimport sys\nprint(sys.version)\n# type sys followed by a dot to see the completions\n"
    # escaped_code = json.dumps(code)  # Escape the string for JavaScript
    # print(escaped_code)
    # window.evaluate_js(f"setCode({escaped_code})")


def receive_all(sock: socket.socket, length: int) -> bytes:
    data = b""
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise ConnectionResetError("Connection closed prematurely")
        data += more
    return data


def receive_messages(api: Api, sock: socket.socket) -> None:
    global _WEB_VEW_ENDED
    while True:
        try:
            # Receive the message length first
            raw_msg_len = receive_all(sock, 4)
            if not raw_msg_len:
                break
            msg_len = struct.unpack("!I", raw_msg_len)[0]

            # Receive the actual message
            data = receive_all(sock, msg_len)
            message = data.decode()
            # sys.stdout.write(f"Received from server: {message}\n")

            json_dict = cast(Dict[str, Any], json.loads(message))
            msg_id = json_dict.get("id")
            sys.stdout.write(f"Received from server with id: {msg_id}\n")

            if msg_id == "destroy":
                api.destroy()
            elif msg_id == "code":
                code = json_dict.get("data", "")
                api.set_code(code)
            elif msg_id == "general_message":
                msg = json_dict.get("data", "")
                sys.stdout.write(f"Received general message: {msg}\n")
        except (ConnectionResetError, struct.error) as err:
            if _WEB_VEW_ENDED:
                sys.stdout.write("receive_messages() Webview ended\n")
            else:
                sys.stderr.write(f"receive_messages() Error receiving message: {err}\n")
            break


def send_message(sock: socket.socket, message: Dict[str, Any]) -> None:
    # Prefix each message with a 4-byte length (network byte order)
    try:
        json_message = json.dumps(message)
        message_bytes = json_message.encode()
        message_length = struct.pack("!I", len(message_bytes))
        sock.sendall(message_length + message_bytes)
    except Exception as e:
        sys.stderr.write(f"Error sending message: {e}\n")


def main():
    global _WEB_VEW_ENDED
    _WEB_VEW_ENDED = False
    doc_id = sys.argv[1]
    port = int(sys.argv[2])

    def on_loaded():
        nonlocal doc_id, client_socket

        sys.stdout.write("Webview is ready\n")
        try:
            data = {
                "id": "webview_ready",
                "doc_id": doc_id,
                "data": "webview_ready",
            }
            send_message(client_socket, data)
            sys.stdout.write("Sent 'webview_ready' to main process\n")
        except Exception as e:
            sys.stderr.write(f"Error sending 'webview_ready': {e}\n")

    try:
        if len(sys.argv) < 3:
            sys.stdout.write("Usage: python shell_edit.py <doc_id>\n")
            sys.exit(1)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", int(port)))

        # Send a message to the main process
        data = {
            "id": "general_message",
            "doc_id": doc_id,
            "data": "Hello from subprocess!",
        }
        send_message(client_socket, data)

        api = Api(doc_id, client_socket, port)
        root = Path(__file__).parent
        html_file = Path(root, "html/index.html")
        sys.stdout.write(f"html_file: {html_file}: Exists: {html_file.exists()}\n")

        # Start a thread to receive messages from the server
        t1 = threading.Thread(
            target=receive_messages,
            args=(
                api,
                client_socket,
            ),
            daemon=True,
        )
        t1.start()

        sys.stdout.write("Creating window\n")
        window = webview.create_window(
            title="Python Editor", url=html_file.as_uri(), js_api=api
        )

        window.events.loaded += on_loaded

        api.set_window(window)
        sys.stdout.write("Window created\n")
        # if sys.platform == "win32":
        #     gui_type = "cef"
        # elif sys.platform == "linux":
        #     gui_type = "qt"
        # else:
        #     gui_type = None

        sys.stdout.write("Starting Webview\n")
        webview.start(
            webview_ready, (window,), gui=None, menu=menu_items
        )  # setting gui is causing crash in LibreOffice
        sys.stdout.write("Ended Webview\n")

        data = {
            "id": "exit",
            "doc_id": doc_id,
            "data": "exit",
        }

        send_message(client_socket, data)
        client_socket.close()
        if t1.is_alive():
            t1.join(timeout=1)
        _WEB_VEW_ENDED = True

    except Exception as e:
        sys.stderr.write(f"Error in main {e}\n")


if __name__ == "__main__":
    main()
