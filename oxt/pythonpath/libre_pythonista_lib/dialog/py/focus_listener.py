from __future__ import annotations
from typing import TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
from com.sun.star.awt import XFocusListener
from ..listener.listener_base import ListenerBase

if TYPE_CHECKING:
    from com.sun.star.awt import FocusEvent
    from .dialog_python import DialogPython


class FocusListener(ListenerBase["DialogPython"], XFocusListener):
    @override
    def focusGained(self, e: FocusEvent) -> None:
        self.component.tk.addKeyHandler(self.component.keyhandler)

    @override
    def focusLost(self, e: FocusEvent) -> None:
        self.component.tk.removeKeyHandler(self.component.keyhandler)
