from __future__ import annotations
from typing import TYPE_CHECKING
import uno
from com.sun.star.awt import XFocusListener
from ..listener.listener_base import ListenerBase

if TYPE_CHECKING:
    from com.sun.star.awt import FocusEvent
    from .dialog_python import DialogPython


class FocusListener(ListenerBase["DialogPython"], XFocusListener):
    def focusGained(self, event: FocusEvent):
        self.component.tk.addKeyHandler(self.component.keyhandler)

    def focusLost(self, event: FocusEvent):
        self.component.tk.removeKeyHandler(self.component.keyhandler)
