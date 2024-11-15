from __future__ import annotations
from typing import Any, Dict, cast
import socket
import struct
import sys
import json
import threading
from pathlib import Path
import webview
import webview.menu as wm
import jedi  # noqa # type: ignore


# https://pywebview.flowrl.com/guide/api.html#webview-settings

webview.settings = {
    "ALLOW_DOWNLOADS": False,
    "ALLOW_FILE_URLS": True,
    "OPEN_EXTERNAL_LINKS_IN_BROWSER": False,
    "OPEN_DEVTOOLS_IN_DEBUG": False,
}

_WEB_VEW_ENDED = False
_IS_DEBUG = False
_IS_DARK_THEME = False
_DARK_THEME_NAME = "material-darker"


class WindowConfig:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = -1
        self.y = -1

    def from_json(self, json_str: str):
        try:
            data = json.loads(json_str)
            self.width = data.get("width", 0)
            self.height = data.get("height", 0)
            self.x = data.get("x", -1)
            self.y = data.get("y", -1)
        except Exception as e:
            sys.stderr.write(f"Error in from_json: {e}\n")

    def from_dict(self, data: Dict[str, int]):
        self.width = data.get("width", 0)
        self.height = data.get("height", 0)
        self.x = data.get("x", -1)
        self.y = data.get("y", -1)

    def to_json(self) -> str:
        data = {"width": self.width, "height": self.height, "x": self.x, "y": self.y}
        return json.dumps(data)

    def to_dict(self) -> Dict[str, int]:
        return {
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
        }

    def has_size(self) -> bool:
        return self.width > 0 and self.height > 0

    def has_position(self) -> bool:
        return self.x > -1 and self.y > -1

    def update_from_api(self, api: Api):
        try:
            if api.has_window():
                api.window_config.width = api._window.width
                api.window_config.height = api._window.height
                api.window_config.x = api._window.x
                api.window_config.y = api._window.y
        except Exception as e:
            sys.stderr.write(f"Error in update_from_api: {e}\n")


class Api:
    def __init__(self, process_id: str, sock: socket.socket, port: int):
        self._window = cast(webview.Window, None)
        self.process_id = process_id
        self.port = port
        self.sock = sock
        self.resources: Dict[str, str] = {}
        self.info: Dict[str, str] = {}
        self.theme: Dict[str, Any] = {}
        self.module_source_code = ""
        self.window_config = WindowConfig()

    def set_window(self, window: webview.Window):
        self._window = window

    def destroy(self):
        global _WEB_VEW_ENDED
        try:
            if self._window:
                # Destroy the window in a separate thread
                # self.hide()
                data = {
                    "cmd": "destroyed",
                    "process_id": self.process_id,
                    "data": {
                        "window_config": self.window_config.to_dict(),
                    },
                }
                send_message(self.sock, data)
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
        global _IS_DEBUG
        try:
            if self._window:
                code = self.get_code()
                if _IS_DEBUG:
                    sys.stdout.write("Code:\n{}\n".format(code))
                data = {
                    "cmd": "code",
                    "process_id": self.process_id,
                    "data": {
                        "code": code,
                        "window_config": self.window_config.to_dict(),
                    },
                }
                send_message(self.sock, data)
                sys.stdout.write("Sent code to server\n")
                self.destroy()

        except Exception as e:
            sys.stderr.write(f"Error in accept: {e}\n")

    def validate_code(self) -> None:
        code = self.get_code()
        request_data = {
            "cmd": "request_action",
            "process_id": self.process_id,
            "action": "validate_code",
            "params": {"code": code},
        }
        send_message(self.sock, request_data)

        # self._window.evaluate_js(
        #     f"alert('{self.resources.get('mbmsg001', 'Code is Valid')}')"
        # )
        sys.stdout.write("Validating code\n")

    def insert_lp_function(self) -> None:
        request_data = {
            "cmd": "request_action",
            "process_id": self.process_id,
            "action": "insert_lp_function",
            "params": {},
        }
        send_message(self.sock, request_data)

    def insert_range(self) -> None:
        request_data = {
            "cmd": "request_action",
            "process_id": self.process_id,
            "action": "insert_range",
            "params": {},
        }
        send_message(self.sock, request_data)

    def log(self, value):
        try:
            code = self.get_code()
            sys.stdout.write("Code:\n{}\n".format(code))
        except Exception as e:
            sys.stderr.write(f"Error in log: {e}")

    def get_autocomplete(self, code, line, column):
        try:
            # sys.stdout.write(f"{code}\n")
            # Combine the additional code with the editor code
            combined_code = self.module_source_code + "\n" + code

            # Adjust the line number for the cursor
            prepended_lines = self.module_source_code.count("\n") + 1
            adjusted_line = line + prepended_lines

            script = jedi.Script(combined_code, path="")
            completions = script.complete(adjusted_line, column)
            suggestions = [completion.name for completion in completions]
            return json.dumps(suggestions)
        except Exception:
            return json.dumps([])

    def has_window(self):
        return self._window is not None

    def get_code(self):
        try:
            if self._window:
                code = self._window.evaluate_js("getCode()")
                return code
        except Exception as e:
            sys.stderr.write(f"Error in get_code: {e}\n")
        return ""

    def set_code(self, code: str):
        try:
            if self._window:
                escaped_code = json.dumps(code)  # Escape the string for JavaScript
                # sys.stdout.write(f"{escaped_code}\n")
                self._window.evaluate_js(f"setCode({escaped_code})")
        except Exception as e:
            sys.stderr.write(f"Error in set_code: {e}\n")

    def insert_text_at_cursor(self, text: str):
        try:
            if self._window:
                js_code = f"insertTextAtCursor('{text}');"
                self._window.evaluate_js(js_code)
        except Exception as e:
            sys.stderr.write(f"Error in insert_text: {e}\n")

    def set_focus_on_editor(self):
        try:
            if self._window:
                js_code = "focusCodeMirror();"
                self._window.evaluate_js(js_code)
        except Exception as e:
            sys.stderr.write(f"Error in set_focus_on_editor: {e}\n")

    def handle_response(self, response: Dict[str, Any]) -> None:
        """
        Handles the response from the server and updates the UI.

        Args:
            response (Dict[str, Any]): The response from the server.
        """
        msg = response.get("message", "")
        status = response.get("status", "")
        try:
            # if msg == "got_resources":
            #     if status == "success":
            #         self.resources = cast(Dict[str, str], response.get("data", {}))

            if msg == "got_info":
                if status == "success":
                    data = cast(Dict[str, Dict[str, str]], response.get("data", {}))
                    self.info = data.get("info", {})
                    self.resources = data.get("resources", {})
                    self.theme = data.get("theme", {})
                    self.module_source_code = cast(
                        str, data.get("module_source_code", "")
                    )
                    self.window_config.from_dict(
                        cast(Dict[str, int], data.get("window_config", {}))
                    )

            elif msg == "validated_code":
                if status == "success":
                    self._window.evaluate_js(
                        f"alert('{self.resources.get('mbmsg001', 'Code is Valid')}')"
                    )
                else:
                    self._window.evaluate_js(
                        f"alert('{self.resources.get('log09', 'Error')}')"
                    )
            elif msg == "lp_fn_inserted":
                if status == "success":
                    data = cast(Dict[str, str], response.get("data", {}))
                    fn_str = data.get("function", "")
                    if fn_str:
                        # self._window.evaluate_js(f"alert('{fn_str}')")
                        self.insert_text_at_cursor(fn_str)
                    else:
                        self._window.evaluate_js(
                            "alert('Failed to insert LP function. No function returned.')"
                        )
            elif msg == "lp_rng_inserted":
                if status == "success":
                    data = cast(Dict[str, str], response.get("data", {}))
                    fn_str = data.get("range", "")
                    if fn_str:
                        # self._window.evaluate_js(f"alert('{fn_str}')")
                        self.insert_text_at_cursor(fn_str)
                    else:
                        self._window.evaluate_js(
                            "alert('Failed to insert range. No function returned.')"
                        )
            elif msg == "pass":
                pass
            else:
                sys.stderr.write(f"Unknown response: {response}\n")
        except Exception as e:
            sys.stderr.write(f"Error handling response: {e}\n")

    def set_theme(self, theme: str):
        try:
            if self._window:
                js_code = f"setCodeMirrorTheme('{theme}');"
                self._window.evaluate_js(js_code)
        except Exception as e:
            sys.stderr.write(f"Error in set_theme: {e}\n")

    def set_body_class(self, class_name: str):
        try:
            if self._window:
                js_code = f"setBodyClass('{class_name}');"
                self._window.evaluate_js(js_code)
        except Exception as e:
            sys.stderr.write(f"Error in set_body_class: {e}\n")

    def append_body_class(self, class_name: str):
        try:
            if self._window:
                js_code = f"appendBodyClass('{class_name}');"
                self._window.evaluate_js(js_code)
        except Exception as e:
            sys.stderr.write(f"Error in append_body_class: {e}\n")

    # region Window Events
    def on_resized(self, width: int, height: int) -> None:
        if _IS_DEBUG:
            sys.stdout.write(f"Resized: {width} x {height}\n")
        self.window_config.width = width
        self.window_config.height = height

    def on_moved(self, x: int, y: int) -> None:
        if _IS_DEBUG:
            sys.stdout.write(f"Moved: {x}, {y}\n")
        # On Ubuntu 24.04, the window position reports 0, 0 when moved
        # It may be the same on other platforms
        self.window_config.x = x
        self.window_config.y = y

    # endregion Window Events


def webview_ready(window: webview.Window):
    global _IS_DARK_THEME
    # code = "# Write your code here! \nimport sys\nprint(sys.version)\n# type sys followed by a dot to see the completions\n"
    # escaped_code = json.dumps(code)  # Escape the string for JavaScript
    # print(escaped_code)
    # window.evaluate_js(f"setCode({escaped_code})")
    if _IS_DARK_THEME:
        window.evaluate_js(f"setCodeMirrorTheme('{_DARK_THEME_NAME}')")
        window.evaluate_js("appendBodyClass('dark')")
    else:
        window.evaluate_js("appendBodyClass('light')")


def receive_all(sock: socket.socket, length: int) -> bytes:
    data = b""
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise ConnectionResetError("Connection closed prematurely")
        data += more
    return data


def receive_messages(
    api: Api, sock: socket.socket, event: threading.Event, stop_event: threading.Event
) -> None:
    global _WEB_VEW_ENDED
    while not stop_event.is_set():
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
            msg_cmd = json_dict.get("cmd")
            sys.stdout.write(f"Received from server with id: {msg_cmd}\n")

            if msg_cmd == "destroy":
                api.destroy()
            elif msg_cmd == "code":
                code = json_dict.get("data", "")
                api.set_code(code)
            elif msg_cmd == "general_message":
                msg = json_dict.get("data", "")
                sys.stdout.write(f"Received general message: {msg}\n")
            elif msg_cmd == "action_completed":
                response = json_dict.get("response_data", {})
                api.handle_response(response)
                event.set()  # Set the event to indicate that the response has been received

            # elif message.startswith("action_completed:"):
            #     response = json.loads(message[len("action_completed:") :])
            #     api.handle_response(response)
            else:
                sys.stdout.write(f"Subprocess received: {message}\n")
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


class Menu:
    def __init__(self, api: Api):
        self.api = api

    def get_menu(self):
        items = [
            wm.Menu(
                self.api.resources.get("mnuCode", "Code"),
                [
                    wm.MenuAction(
                        cast(str, self.api.resources.get("mnuValidate", "Validate")),
                        self.api.validate_code,
                    ),  # type: ignore
                ],
            ),
            wm.Menu(
                self.api.resources.get("mnuInsert", "Insert"),
                [
                    wm.MenuAction(
                        cast(
                            str,
                            self.api.resources.get("mnuAutoLpFn", "Insert Lp Function"),
                        ),
                        self.api.insert_lp_function,
                    ),  # type: ignore
                    wm.MenuAction(
                        cast(
                            str,
                            self.api.resources.get("mnuSelectRng", "Select Range"),
                        ),
                        self.api.insert_range,
                    ),  # type: ignore
                ],
            ),
        ]
        return items


def main():
    global _WEB_VEW_ENDED, _IS_DEBUG, _IS_DARK_THEME
    _WEB_VEW_ENDED = False
    _IS_DEBUG = False
    process_id = sys.argv[1]
    port = int(sys.argv[2])
    try:
        if len(sys.argv) > 3:
            _IS_DEBUG = sys.argv[3] == "debug"
    except Exception:
        pass

    def on_loaded():
        nonlocal process_id, client_socket

        sys.stdout.write("Webview is ready\n")
        try:
            data = {
                "cmd": "webview_ready",
                "process_id": process_id,
                "data": "webview_ready",
            }
            send_message(client_socket, data)
            sys.stdout.write("Sent 'webview_ready' to main process\n")
        except Exception as e:
            sys.stderr.write(f"Error sending 'webview_ready': {e}\n")

    try:
        if len(sys.argv) < 3:
            sys.stdout.write("Usage: python shell_edit.py <process_id> <port>\n")
            sys.exit(1)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", int(port)))

        # Send a message to the main process
        data = {
            "cmd": "general_message",
            "process_id": process_id,
            "data": "Hello from subprocess!",
        }
        send_message(client_socket, data)

        api = Api(process_id, client_socket, port)
        root = Path(__file__).parent
        html_file = Path(root, "html/index.html")
        sys.stdout.write(f"html_file: {html_file}: Exists: {html_file.exists()}\n")

        # Create an event to wait for the menu data
        info_event = threading.Event()
        stop_event = threading.Event()

        # Start a thread to receive messages from the server
        t1 = threading.Thread(
            target=receive_messages,
            args=(api, client_socket, info_event, stop_event),
            daemon=True,
        )
        t1.start()

        # Request menu data from the server
        request_data = {
            "cmd": "request_action",
            "process_id": process_id,
            "action": "get_info",
            "params": {},
        }
        send_message(client_socket, request_data)
        sys.stdout.write("Requested menu data from server\n")

        # Wait for the menu data to be received
        info_event.wait(timeout=10)  # Wait for up to 10 seconds

        if api.resources:
            sys.stdout.write(f"Received menu data: {api.resources}\n")
        else:
            sys.stderr.write("Failed to receive menu data within the timeout period\n")

        if api.info:
            sys.stdout.write(f"Received info data: {api.info}\n")
        else:
            sys.stderr.write("Failed to receive info data within the timeout period\n")

        if api.theme:
            sys.stdout.write(f"Received theme data: {api.theme}\n")
        else:
            sys.stderr.write("Failed to receive theme data within the timeout period\n")

        # if api.module_source_code:
        #     sys.stdout.write(f"Received Module Source Code: {api.module_source_code}\n")

        _IS_DARK_THEME = bool(api.theme.get("is_doc_dark", False))

        sys.stdout.write("Creating window\n")
        title = api.resources.get("title10", "Python Code")
        cell = api.info.get("cell", "")
        if cell:
            title = f"{title} - {cell}"
        if api.window_config.has_size():
            width = api.window_config.width
            height = api.window_config.height
        else:
            width = 800
            height = 600

        if api.window_config.has_position():
            x = api.window_config.x
            y = api.window_config.y
        else:
            x = None
            y = None
        window = webview.create_window(
            title=title,
            url=html_file.as_uri(),
            width=width,
            height=height,
            x=x,
            y=y,
            js_api=api,
        )

        window.events.loaded += on_loaded
        window.events.moved += api.on_moved
        window.events.resized += api.on_resized

        api.set_window(window)
        sys.stdout.write("Window created\n")
        # if sys.platform == "win32":
        #     gui_type = "cef"
        # elif sys.platform == "linux":
        #     gui_type = "qt"
        # else:
        #     gui_type = None

        sys.stdout.write("Starting Webview\n")
        mnu = Menu(api)
        webview.start(
            webview_ready, (window,), gui=None, menu=mnu.get_menu()
        )  # setting gui is causing crash in LibreOffice
        sys.stdout.write("Ended Webview\n")

        data = {
            "cmd": "exit",
            "process_id": process_id,
            "data": {"window_config": api.window_config.to_dict()},
        }

        send_message(client_socket, data)
        _WEB_VEW_ENDED = True
        stop_event.set()
        if t1.is_alive():
            t1.join(timeout=1)
        client_socket.close()

    except Exception as e:
        sys.stderr.write(f"Error in main {e}\n")


if __name__ == "__main__":
    main()
