from __future__ import annotations
from typing import cast, TYPE_CHECKING

# import multiprocessing
from multiprocessing.connection import Connection
import sys
import json
import threading
from pathlib import Path
import webview
import jedi

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


class Api:
    def __init__(self, doc_id: str, child_conn: Connection):
        self._window = cast(webview.Window, None)
        self._doc_id = doc_id
        self.child_conn = child_conn

    def set_window(self, window: webview.Window):
        self._window = window

    def destroy(self):
        try:
            if self._window:
                # Destroy the window in a separate thread
                # self.hide()
                self._window.destroy()
                self._window = cast(webview.Window, None)
        except Exception as e:
            print("Error in destroy", e)

    def hide(self):
        try:
            if self._window:
                if not self._window.hidden:
                    print("Hiding window")
                    self._window.hide()
                    print("Window hidden")
                else:
                    print("Window already hidden")
        except Exception as e:
            print("Error in hide", e)

    def show(self):
        try:
            if self._window:
                print("Showing window")
                self._window.show()
                print("Window shown")
        except Exception as e:
            print("Error in show", e)

    def accept(self) -> None:
        try:
            if self._window:
                code = self._window.evaluate_js("getCode()")
                print("Code:\n{}".format(code))
                self.child_conn.send("Code:\n{}".format(code))  # noqa: F821 # type: ignore

        except Exception as e:
            print("Error in accept", e)

    def log(self, value):
        try:
            code = self._window.evaluate_js("getCode()")
            print("Code:\n{}".format(code))
        except Exception as e:
            print("Error in log", e)

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
                print(escaped_code)
                self._window.evaluate_js(f"setCode({escaped_code})")
        except Exception as e:
            print("Error in set_code", e)


def webview_ready(window: webview.Window):
    pass
    # code = "# Write your code here! \nimport sys\nprint(sys.version)\n# type sys followed by a dot to see the completions\n"
    # escaped_code = json.dumps(code)  # Escape the string for JavaScript
    # print(escaped_code)
    # window.evaluate_js(f"setCode({escaped_code})")


def read_messages(api: Api, child_conn: Connection):
    try:
        while True:
            message: str = child_conn.recv()
            print(f"Subprocess received: {message}")
            # Handle the message
            if message == "destroy":
                api.destroy()
            elif message.startswith("set_code:"):
                msg = message.removeprefix("set_code:").lstrip()
                # Perform some action
                api.set_code(msg)
            # Add more message handling as needed
    except EOFError:
        print("Connection closed by main process.")


def main():
    def on_loaded():
        print("Webview is ready")
        try:
            child_conn.send("webview_ready")
            print("Sent 'webview_ready' to main process")
        except Exception as e:
            print(f"Error sending 'webview_ready': {e}")

    try:
        if len(sys.argv) < 3:
            print("Usage: python shell_edit.py <doc_id>")
            sys.exit(1)
        doc_id = sys.argv[1]
        child_conn_fd = int(sys.argv[2])

        # Retrieve the file descriptor from the environment
        # child_conn_fd = int(os.environ["CHILD_CONN_FD"])

        # Create the connection object from the file descriptor
        child_conn = Connection(child_conn_fd)

        # Send a message to the main process
        child_conn.send("Hello from subprocess!")

        api = Api(doc_id, child_conn)
        root = Path(__file__).parent
        html_file = Path(root, "html/index.html")
        print(f"html_file: {html_file}: Exists: {html_file.exists()}")

        print("Creating window")
        window = webview.create_window(
            title="Python Editor", url=html_file.as_uri(), js_api=api
        )

        window.events.loaded += on_loaded

        api.set_window(window)
        print("Window created")
        # if sys.platform == "win32":
        #     gui_type = "cef"
        # elif sys.platform == "linux":
        #     gui_type = "qt"
        # else:
        #     gui_type = None

        # Pass child_conn to read_messages
        threading.Thread(
            target=read_messages, args=(api, child_conn), daemon=True
        ).start()

        print("Starting Webview")
        webview.start(
            webview_ready, (window,), gui=None, menu=menu_items
        )  # setting gui is causing crash in LibreOffice

        print("Ended Webview")
    except Exception as e:
        print("Error in main", e)


if __name__ == "__main__":
    main()
