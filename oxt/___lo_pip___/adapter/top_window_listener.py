from __future__ import annotations
from typing import cast, TYPE_CHECKING

import uno
from .adapter_base import AdapterBase, GenericArgs
from ..lo_util.util import Util

from com.sun.star.awt import XExtendedToolkit
from com.sun.star.awt import XTopWindowListener

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject


class TopWindowListener(AdapterBase, XTopWindowListener):
    """
    Makes it possible to receive window events.

    See Also:
        `API XTopWindowListener <https://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1awt_1_1XTopWindowListener.html>`_
    """

    def __init__(self, trigger_args: GenericArgs | None = None, add_listener: bool = True) -> None:
        """
        Constructor:

        Arguments:
            add_listener (bool, optional): If ``True`` listener is automatically added. Default ``True``.
            trigger_args (GenericArgs, optional): Args that are passed to events when they are triggered.
        """
        super().__init__(trigger_args=trigger_args)
        # assigning tk to class is important.
        # if not assigned then tk goes out of scope after class __init__() is called
        # and dispose is called right after __init__()
        self._tk = None
        if add_listener:
            util = Util()
            self._tk = cast(XExtendedToolkit, util.create_uno_service("com.sun.star.awt.Toolkit"))
            if self._tk is not None:
                self._tk.addTopWindowListener(self)

    def __del__(self):
        if self._tk:
            self._tk.removeTopWindowListener(self)

    def windowOpened(self, event: EventObject) -> None:
        """Is invoked when a window is activated."""
        self._trigger_event("windowOpened", event)

    def windowActivated(self, event: EventObject) -> None:
        """Is invoked when a window is activated."""
        self._trigger_event("windowActivated", event)

    def windowDeactivated(self, event: EventObject) -> None:
        """Is invoked when a window is deactivated."""
        self._trigger_event("windowDeactivated", event)

    def windowMinimized(self, event: EventObject) -> None:
        """is invoked when a window is iconified."""
        self._trigger_event("windowMinimized", event)

    def windowNormalized(self, event: EventObject) -> None:
        """Is invoked when a window is deiconified."""
        self._trigger_event("windowNormalized", event)

    def windowClosing(self, event: EventObject) -> None:
        """
        Is invoked when a window is in the process of being closed.

        The close operation can be overridden at this point.
        """
        self._trigger_event("windowClosing", event)

    def windowClosed(self, event: EventObject) -> None:
        """Is invoked when a window has been closed."""
        self._trigger_event("windowClosed", event)

    def disposing(self, event: EventObject) -> None:
        """
        Gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including ``XComponent.removeEventListener()`` ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at ``XComponent``.
        """
        # from com.sun.star.lang.XEventListener
        self._trigger_event("disposing", event)
