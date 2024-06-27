from __future__ import annotations
import time
from typing import Any, cast, TYPE_CHECKING

import uno
import unohelper
from com.sun.star.awt import XTopWindowListener
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import TOP
from com.sun.star.awt import Rectangle
from com.sun.star.awt import MenuItemStyle
from com.sun.star.awt import WindowAttribute
from com.sun.star.awt import VclWindowPeerAttribute
from com.sun.star.awt import XMenuListener

if TYPE_CHECKING:
    from com.sun.star.script.provider import XScriptContext
    from com.sun.star.awt import MenuBar  # service
    from com.sun.star.awt import MenuEvent  # struct
    from com.sun.star.lang import EventObject  # struct
    from com.sun.star.frame import Frame  # service
    from com.sun.star.awt import Toolkit  # service
    from com.sun.star.awt import PopupMenu  # service
    from ..window_type import WindowType


class DialogMb(XTopWindowListener, XMenuListener, unohelper.Base):
    FONT = "DejaVu Sans Mono"
    MARGIN = 3
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 26
    WIDTH = 600
    NB_TAB = 4
    HEADER = 30  # can create space for menus at the top
    FOOTER = 40
    HEIGHT = 310
    MIN_HEIGHT = HEADER + FOOTER + 30
    MIN_WIDTH = 225

    def __init__(self, script_ctx: XScriptContext) -> None:
        XTopWindowListener.__init__(self)
        XMenuListener.__init__(self)
        unohelper.Base.__init__(self)
        self._ctx = script_ctx.getComponentContext()
        self._srv_mgr = self._ctx.getServiceManager()
        self._disposed = False
        self._width = DialogMb.WIDTH
        self._height = DialogMb.HEIGHT
        self._current_tab_index = 1
        self._padding = 14
        self._width = DialogMb.WIDTH
        self._height = DialogMb.HEIGHT
        self._btn_width = DialogMb.BUTTON_WIDTH
        self._btn_height = DialogMb.BUTTON_HEIGHT
        self._margin = DialogMb.MARGIN
        self._frame = None

        self._mb = cast("MenuBar", None)
        try:
            self.tk = cast("Toolkit", self._srv_mgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self._ctx))
            self._init_dialog()
            self._add_frame()
            self._add_menu_bar()
            self._dialog.addTopWindowListener(self)

        except Exception as e:
            print(e)

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        rect = Rectangle()
        rect.Width = self._width
        rect.Height = self._height

        rect.X = 100
        rect.Y = 100

        desc = WindowDescriptor()
        desc.Type = TOP
        desc.WindowServiceName = "window"
        desc.ParentIndex = -1
        desc.Parent = None  # type: ignore
        desc.Bounds = rect

        desc.WindowAttributes = (
            WindowAttribute.SHOW
            + WindowAttribute.BORDER
            + WindowAttribute.SIZEABLE
            + WindowAttribute.MOVEABLE
            + VclWindowPeerAttribute.CLIPCHILDREN
        )

        dialog_peer = self.tk.createWindow(desc)

        self._dialog = cast("WindowType", dialog_peer)

    def _add_frame(self) -> None:
        """Add frame to dialog"""
        # create new empty frame and set window on it
        frame = cast("Frame", self._srv_mgr.createInstanceWithContext("com.sun.star.frame.Frame", self._ctx))
        frame.setName("DialogMb_Frame")
        frame.initialize(self._dialog)

        self._frame = frame

    # region XTopWindowListener
    def windowOpened(self, event: EventObject) -> None:
        """is invoked when a window is activated."""
        print("Window Opened")

    def windowActivated(self, event: EventObject) -> None:
        """is invoked when a window is activated."""

        print("Window Activated")

    def windowDeactivated(self, event: EventObject) -> None:
        """is invoked when a window is deactivated."""
        print("Window De-activated")

    def windowMinimized(self, event: EventObject) -> None:
        """Is invoked when a window is iconified."""
        print("Window Minimized")

    def windowNormalized(self, event: EventObject) -> None:
        """is invoked when a window is deiconified."""
        print("Window Normalized")

    def windowClosing(self, event: EventObject) -> None:
        """
        is invoked when a window is in the process of being closed.

        The close operation can be overridden at this point.
        """
        print("Window Closing")
        self._is_shown = False

    def windowClosed(self, event: EventObject) -> None:
        """is invoked when a window has been closed."""
        print("Window Closed")

    def disposing(self, event: EventObject) -> None:

        print("Disposing")
        if not self._disposed:
            try:
                self._disposed = True
                self._dialog.removeTopWindowListener(self)
                self._dialog.setMenuBar(None)  # type: ignore
                self._mb = None
                self._dialog.dispose()
            except Exception as e:
                print("Error in disposing", e)

    # endregion XTopWindowListener

    # region XMenuListener
    def itemActivated(self, event: MenuEvent) -> None:
        print("Item Activated", event.MenuId)

    def itemDeactivated(self, event: MenuEvent) -> None:
        print("Item De-Activated", event.MenuId)

    def itemHighlighted(self, event: MenuEvent) -> None:
        print("Item Highlighted", event.MenuId)

    def itemSelected(self, event: MenuEvent) -> None:
        print("Item Selected", event.MenuId)

    # endregion XMenuListener

    # region Menubar
    def _get_popup_menu(self):

        # https://wiki.documentfoundation.org/Documentation/DevGuide/Graphical_User_Interfaces#The_Toolkit_Service
        try:
            pm = cast("PopupMenu", self._srv_mgr.createInstanceWithContext("com.sun.star.awt.PopupMenu", self._ctx))
            pm.insertItem(1, "~First Entry", 0, 0)
            pm.insertItem(2, "First Radio Entry", MenuItemStyle.RADIOCHECK + MenuItemStyle.AUTOCHECK, 1)
            pm.insertItem(3, "Second Radio Entry", MenuItemStyle.RADIOCHECK + MenuItemStyle.AUTOCHECK, 2)
            pm.insertItem(4, "Third RadioEntry", MenuItemStyle.RADIOCHECK + MenuItemStyle.AUTOCHECK, 3)
            pm.insertSeparator(5)
            pm.insertItem(6, "Fifth Entry", MenuItemStyle.CHECKABLE + MenuItemStyle.AUTOCHECK, 5)
            pm.insertItem(7, "Fourth Entry", MenuItemStyle.CHECKABLE + MenuItemStyle.AUTOCHECK, 6)
            pm.insertItem(8, "Sixth Entry", 0, 9)
            pm.insertItem(9, "Close Dialog", 0, 10)

            pm.enableItem(2, False)
            pm.checkItem(3, True)
            return pm

        except Exception as e:
            print(e)
        return None

    def _add_menu_bar(self) -> None:
        pm = self._get_popup_menu()
        if pm is None:
            print("_add_menu_bar() No popup menu found. Exiting.")
            return
        mb = cast("MenuBar", self._srv_mgr.createInstanceWithContext("com.sun.star.awt.MenuBar", self._ctx))
        mb.insertItem(1, "~First MenuBar Item", MenuItemStyle.AUTOCHECK, 0)
        mb.insertItem(2, "~Second MenuBar Item", MenuItemStyle.AUTOCHECK, 1)
        pm.addMenuListener(self)
        mb.setPopupMenu(1, pm)  # type: ignore
        self._mb = mb
        self._dialog.setMenuBar(mb)

    # endregion Menubar
