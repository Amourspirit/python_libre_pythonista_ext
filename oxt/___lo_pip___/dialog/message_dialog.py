from __future__ import annotations
from typing import Any, cast

import uno

from .dialog_base import DialogBase

from com.sun.star.awt.MessageBoxType import MESSAGEBOX
from com.sun.star.awt import XWindowPeer
from com.sun.star.awt import XMessageBoxFactory


class MessageDialog(DialogBase):
    """Shows message in standard message box."""

    def __init__(self, ctx: Any, parent: XWindowPeer, **kwargs):
        super().__init__(ctx)
        self.parent = parent
        self.args = kwargs

    def execute(self):
        box_type = self.args.get("type", MESSAGEBOX)
        buttons = int(self.args.get("buttons", 1))
        title = str(self.args.get("title", ""))
        message = str(self.args.get("message", ""))
        toolkit = cast(XMessageBoxFactory, self.parent.getToolkit())
        dialog = toolkit.createMessageBox(self.parent, box_type, buttons, title, message)
        n = dialog.execute()
        dialog.dispose()  # type: ignore
        return n
