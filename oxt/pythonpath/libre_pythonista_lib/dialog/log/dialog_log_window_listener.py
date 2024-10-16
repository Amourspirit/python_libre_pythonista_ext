from __future__ import annotations
from typing import TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
from com.sun.star.awt import XWindowListener
from ..listener.listener_base import ListenerBase

if TYPE_CHECKING:
    from com.sun.star.awt import WindowEvent
    from .dialog_log import DialogLog

# Component events are provided only for notification purposes.
# Moves and resizes will be handled internally by the window component, so that GUI layout works properly regardless
# of whether a program registers such a listener or not.


class DialogLogWindowListener(ListenerBase["DialogLog"], XWindowListener):
    """WindowListener for DialogLog."""

    @override
    def windowResized(self, e: WindowEvent) -> None:
        # src = cast("WindowType", event.Source)
        # size = src.Size
        # margin = self.component.MARGIN

        # print(src.Windows[0])
        # width = size.Width - margin * 2
        # height = size.Height - margin * 3
        # src.Windows[0].setPosSize(0, 0, width, height, PosSize.SIZE)
        self.component.resize()
