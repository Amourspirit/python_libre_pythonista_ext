from __future__ import annotations
from typing import cast, TYPE_CHECKING
import sys
import webview
import jedi
import json
from pathlib import Path

try:
    from .menu import menu_items
except ImportError:
    from menu import menu_items

# https://pywebview.flowrl.com/guide/api.html#webview-settings

webview.settings = {
    "ALLOW_DOWNLOADS": False,
    "ALLOW_FILE_URLS": True,
    "OPEN_EXTERNAL_LINKS_IN_BROWSER": True,
    "OPEN_DEVTOOLS_IN_DEBUG": False,
}


class Api:
    def __init__(self):
        self._window = cast(webview.Window, None)

    def set_window(self, window: webview.Window):
        self._window = window

    def destroy(self):
        if self._window:
            self._window.destroy()
        self._window = cast(webview.Window, None)
        # this is needed in linux but not in windows.
        sys.exit()

    def log(self, value):
        code = self._window.evaluate_js("getCode()")
        print("Code:\n{}".format(code))

    def get_autocomplete(self, code, line, column):
        try:
            code = self._window.evaluate_js("getCode()")
            print("code:\n", code)
            script = jedi.Script(code, path="")
            print("script:\n", script)
            completions = script.complete(line, column)
            suggestions = [completion.name for completion in completions]
            print()
            print("Suggestions:\n", suggestions)
            return json.dumps(suggestions)
        except Exception:
            return json.dumps([])


def find_src_dir():
    current_path = Path.cwd()
    while current_path != current_path.root:
        if (current_path / "src").exists():
            return current_path / "src"
        current_path = current_path.parent
    return None


def set_code(window: webview.Window):
    code = "# Write your code here! \nimport sys\nprint(sys.version)\n# type sys followed by a dot to see the completions\n"
    escaped_code = json.dumps(code)  # Escape the string for JavaScript
    print(escaped_code)
    window.evaluate_js(f"setCode({escaped_code})")


def main():
    root = Path(__file__).parent
    html_file = Path(root, "html/index.html")

    api = Api()
    window = webview.create_window(
        title="Python Editor",
        url=html_file.as_uri(),
        js_api=api,
    )
    api.set_window(window)
    if sys.platform == "win32":
        gui_type = "cef"
    elif sys.platform == "linux":
        gui_type = "qt"
    else:
        gui_type = None
    webview.start(set_code, (window,), gui=gui_type, menu=menu_items)
    print("Ended Webview")


if __name__ == "__main__":
    main()
