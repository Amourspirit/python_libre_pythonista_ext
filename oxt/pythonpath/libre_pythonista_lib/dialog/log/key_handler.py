from __future__ import annotations
from typing import TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
from com.sun.star.awt import XKeyHandler
from ..listener.listener_base import ListenerBase

if TYPE_CHECKING:
    from com.sun.star.awt import KeyEvent
    from .dialog_log import DialogLog


class KeyHandler(ListenerBase["DialogLog"], XKeyHandler):
    """KeyHandler for DialogPython."""

    @override
    def keyPressed(self, aEvent: KeyEvent) -> bool:
        try:
            attr = f"onkey_{aEvent.KeyCode}"
            # print("KeyHandler: keyPressed: attr", attr)
            # print(event.KeyCode, event.Modifiers)
            return getattr(self.component, attr)(aEvent.Modifiers)
        except AttributeError:
            # print("KeyHandler: keyPressed: AttributeError")
            return False

    @override
    def keyReleased(self, aEvent: KeyEvent) -> bool:
        return False
