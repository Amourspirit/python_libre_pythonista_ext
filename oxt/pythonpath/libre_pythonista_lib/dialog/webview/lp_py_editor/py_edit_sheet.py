from __future__ import annotations
from typing import TYPE_CHECKING

import webview

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PyEditSheet:
    def __init__(self, sheet: str, cell: str) -> None:
        self._sheet = sheet
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._window = None

    def show(self) -> None:
        self._log.debug("Starting webview")
        try:
            self._window = webview.create_window("Woah dude!", "https://example.com")  # type: ignore
            webview.start()  # type: ignore
        except Exception as e:
            self._log.exception(f"Error: {e}")
