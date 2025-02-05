# region Imports
from __future__ import annotations
from typing import TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper

from ooodev.calc import CalcDoc

from com.sun.star.awt import XTopWindowListener
from ...const import DISPATCH_SEL_RNG
from ...menus import menu_util as mu

if TYPE_CHECKING:
    # only need types in design time and not at run time.
    from com.sun.star.lang import EventObject
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
# endregion Imports

# region DocWindow Class


class TopListenerRng(XTopWindowListener, unohelper.Base):
    """
    This listener is automatically attached to active spreadsheet by the DialogPython class.
    It is attached when the Dialog select cell range is invoked.

    The job of this class is to simply invoke the range selection dialog as soon as the Calc
    window is activated.
    Upon Activation this class removes itself as a listener and invokes the range selection dialog.
    """

    def __init__(self, doc: CalcDoc) -> None:
        XTopWindowListener.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        # assigning tk to class is important.
        # if not assigned then tk goes out of scope after class __init__() is called
        # and dispose is called right after __init__()
        self._doc = doc
        try:
            self._top = self._doc.get_top_window()
            self._top.addTopWindowListener(self)  # type: ignore
        except Exception:
            self._log.error("Error adding listener to calc doc.", exc_info=True)

    @override
    def windowOpened(self, e: EventObject) -> None:
        """is invoked when a window is activated."""
        pass

    @override
    def windowActivated(self, e: EventObject) -> None:
        """is invoked when a window is activated."""
        with self._log.indent(True):
            self._log.debug("Window Activated")
            self._top.removeTopWindowListener(self)  # type: ignore
            self._log.debug("Top Listener Removed")
            try:
                # self._doc.dispatch_cmd(".uno:About")
                mu.dispatch_cs_cmd(
                    DISPATCH_SEL_RNG,
                    in_thread=False,
                    url=mu.get_url_from_command(DISPATCH_SEL_RNG),
                    log=self._log,
                )
                # self._doc.dispatch_cmd(DISPATCH_SEL_RNG)
                # Lo.dispatch_cmd(DISPATCH_SEL_RNG, in_thread=True)
                # self._doc.invoke_range_selection()
                self._log.debug("invoke_range_selection()")
            except Exception:
                self._log.error("Error getting range from popup.", exc_info=True)

    @override
    def windowDeactivated(self, e: EventObject) -> None:
        """is invoked when a window is deactivated."""
        with self._log.indent(True):
            self._log.debug("Window De-activated")

    @override
    def windowMinimized(self, e: EventObject) -> None:
        """Is invoked when a window is iconified."""
        with self._log.indent(True):
            self._log.debug("Window Minimized")

    @override
    def windowNormalized(self, e: EventObject) -> None:
        """is invoked when a window is deiconified."""
        with self._log.indent(True):
            self._log.debug("Window Normalized")

    @override
    def windowClosing(self, e: EventObject) -> None:
        """
        is invoked when a window is in the process of being closed.

        The close operation can be overridden at this point.
        """
        with self._log.indent(True):
            self._log.debug("Window Closing")

    @override
    def windowClosed(self, e: EventObject) -> None:
        """is invoked when a window has been closed."""
        with self._log.indent(True):
            self._log.debug("Window Closed")

    @override
    def disposing(self, Source: EventObject) -> None:  # noqa: N803
        """
        gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including XComponent.removeEventListener() ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at XComponent.
        """

        # don't expect Disposing to print if script ends due to closing.
        # script will stop before dispose is called
        with self._log.indent(True):
            self._log.debug("Disposing")


# endregion DocWindow Class
