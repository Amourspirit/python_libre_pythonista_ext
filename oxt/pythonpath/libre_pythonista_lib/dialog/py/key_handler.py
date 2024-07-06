from __future__ import annotations
from typing import cast, TYPE_CHECKING
import uno
from com.sun.star.awt import XKeyHandler
from ..listener.listener_base import ListenerBase

if TYPE_CHECKING:
    from com.sun.star.awt import KeyEvent
    from .dialog_mb import DialogMb


class KeyHandler(ListenerBase["DialogMb"], XKeyHandler):
    """KeyHandler for DialogMb."""

    def keyPressed(self, event: KeyEvent) -> bool:
        try:
            attr = f"onkey_{event.KeyCode}"
            # print("KeyHandler: keyPressed: attr", attr)
            # print(event.KeyCode, event.Modifiers)
            return getattr(self.component, attr)(event.Modifiers)
        except AttributeError:
            # print("KeyHandler: keyPressed: AttributeError")
            return False

    def keyReleased(self, event: KeyEvent) -> bool:
        return False
