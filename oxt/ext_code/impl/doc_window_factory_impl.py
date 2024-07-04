from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple
import contextlib

import uno
import unohelper
from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import XSingleComponentFactory


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from com.sun.star.uno import XInterface
    from com.sun.star.uno import XComponentContext
    from com.sun.star.awt import UnoControlDialog  # service
    from ...pythonpath.libre_pythonista_lib.dialog.handlers.log_win_handler import LogWinHandler
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from libre_pythonista_lib.dialog.handlers.log_win_handler import LogWinHandler


# https://forum.openoffice.org/en/forum/viewtopic.php?p=295118


class DockingWindowFactoryImpl(XServiceInfo, XSingleComponentFactory, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.DockingWindowFactory"
    SERVICE_NAMES = (IMPLE_NAME,)

    def __init__(self, ctx, *args):
        XServiceInfo.__init__(self)
        XSingleComponentFactory.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx

    # region XSingleComponentFactory

    def createInstanceWithArgumentsAndContext(self, args: Tuple[Any, ...], ctx: XComponentContext) -> XInterface:
        """
        Creates an instance of a component and initializes the new instance with the given arguments and context.

        Raises:
            com.sun.star.uno.Exception: ``Exception``
        """
        try:
            return create_window(ctx, args)
        except Exception as e:
            print(e)

    def createInstanceWithContext(self, ctx: XComponentContext) -> XInterface:
        """
        Creates an instance of a service implementation.

        Raises:
            com.sun.star.uno.Exception: ``Exception``
        """
        return self.createInstanceWithArgumentsAndContext((), ctx)

    # endregion XSingleComponentFactory

    # region XServiceInfo
    def getImplementationName(self) -> str:
        """
        Provides the implementation name of the service implementation.
        """
        return self.IMPLE_NAME

    def getSupportedServiceNames(self) -> Tuple[str, ...]:
        """
        Provides the supported service names of the implementation, including also indirect service names.
        """
        return self.SERVICE_NAMES

    def supportsService(self, name: str) -> bool:
        """
        Tests whether the specified service is supported, i.e.

        implemented by the implementation.
        """
        return name in self.SERVICE_NAMES

    # endregion XServiceInfo

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)


def createInstance(ctx):
    return DockingWindowFactoryImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    createInstance, DockingWindowFactoryImpl.IMPLE_NAME, DockingWindowFactoryImpl.SERVICE_NAMES
)


from com.sun.star.awt import WindowDescriptor, Rectangle
from com.sun.star.awt import XActionListener
from com.sun.star.awt import XWindowListener
from com.sun.star.awt.PosSize import POS, SIZE
from com.sun.star.awt.VclWindowPeerAttribute import CLIPCHILDREN
from com.sun.star.awt.WindowAttribute import SHOW, BORDER, SIZEABLE, MOVEABLE, CLOSEABLE
from com.sun.star.awt.WindowClass import SIMPLE
from com.sun.star.beans import NamedValue
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.task import XJobExecutor


# Valid resource URL for docking window starts with
# private:resource/dockingwindow. And valid name for them are
# 9800 - 9809 (only 10 docking windows can be created).
# See lcl_checkDockingWindowID function defined in
# source/sfx2/source/dialog/dockwin.cxx.
# If the name of dockingwindow conflict with other windows provided by
# other extensions, strange result would be happen.
# https://github.com/LibreOffice/core/blob/3c91fb758a429f51b89dfe9cea088691ced6d0c1/sfx2/source/dialog/dockwin.cxx#L292

RESOURCE_URL = "private:resource/dockingwindow/___float_dialog_error_num___"

# EXT_ID = "___lo_identifier___"


def create_window(ctx: Any, args: Tuple[Any, ...]) -> Any:
    """Creates docking window.

    Args:
        ctx: component context
        args: arguments passed by the window content factory manager.


    Returns:
        new docking window
    """
    global _CONDITIONS_MET

    def create(name):
        return ctx.getServiceManager().createInstanceWithContext(name, ctx)

    if not args:
        return None

    frame = None  # frame of parent document window
    for arg in args:
        name = arg.Name
        if name == "ResourceURL":
            if arg.Value != RESOURCE_URL:
                return None
        elif name == "Frame":
            frame = arg.Value

    if frame is None:
        return None  # ToDo: raise exception

    # this dialog has no title and placed at the top left corner.
    dialog1 = "vnd.sun.star.extension://___lo_identifier___/___float_dialog_error___"
    window = None
    if True:
        toolkit = create("com.sun.star.awt.Toolkit")
        parent = frame.getContainerWindow()

        # Creates outer window
        # title name of this window is defined in WindowState configuration.
        desc = WindowDescriptor(
            SIMPLE,
            "window",
            parent,
            0,
            Rectangle(0, 0, 100, 100),
            SHOW | SIZEABLE | MOVEABLE | CLOSEABLE | CLIPCHILDREN,
        )
        window = toolkit.createWindow(desc)

        # Create inner window from dialog
        dp = create("com.sun.star.awt.ContainerWindowProvider")
        child = cast("UnoControlDialog", dp.createContainerWindow(dialog1, "", window, None))
        if not _CONDITIONS_MET:
            child.setVisible(True)
            return window
        handler = LogWinHandler(ctx, child)
        child.setVisible(True)
        # child.setPosSize(0, 0, 0, 0, POS)  # if the dialog is not placed at
        # top left corner
        window.addWindowListener(WindowResizeListener(handler))
    return window


# for normal window based dockingwindow


class WindowResizeListener(XWindowListener, unohelper.Base):

    def __init__(self, handler: LogWinHandler):
        XWindowListener.__init__(self)
        unohelper.Base.__init__(self)
        self.handler = handler

    def disposing(self, ev):
        pass

    # XWindowListener
    def windowMoved(self, ev):
        pass

    def windowShown(self, ev):
        pass

    def windowHidden(self, ev):
        pass

    def windowResized(self, ev):
        # extends inner window to match with the outer window
        if self.handler:
            self.handler.dialog.setPosSize(0, 0, ev.Width, ev.Height, SIZE)
            self.handler.resize(ev.Width, ev.Height)
            # ToDo: resize dialog elements


# Tool functions


def create_service(ctx, name, args=None):
    """Create service with args if required."""
    smgr = ctx.getServiceManager()
    if args:
        return smgr.createInstanceWithArgumentsAndContext(name, args, ctx)
    else:
        return smgr.createInstanceWithContext(name, ctx)


from com.sun.star.awt import Rectangle


def show_message(ctx, peer, message, title="", type="messbox", buttons=1):
    """Show text in message box."""
    older_imple = check_method_parameter(
        ctx, "com.sun.star.awt.XMessageBoxFactory", "createMessageBox", 1, "com.sun.star.awt.Rectangle"
    )

    if older_imple:
        box = peer.getToolkit().createMessageBox(peer, Rectangle(), type, buttons, title, message)
    else:
        name = {
            "messbox": "MESSAGEBOX",
            "infobox": "INFOBOX",
            "warningbox": "WARNINGBOX",
            "errorbox": "ERRORBOX",
            "querybox": "QUERYBOX",
        }[type]
        _type = uno.getConstantByName("com.sun.star.awt.MessageBoxType." + name)
        box = peer.getToolkit().createMessageBox(peer, _type, buttons, title, message)
    n = box.execute()
    box.dispose()
    return n


def check_method_parameter(ctx, interface_name, method_name, param_index, param_type):
    """Check the method has specific type parameter at the specific position."""
    cr = create_service(ctx, "com.sun.star.reflection.CoreReflection")
    try:
        idl = cr.forName(interface_name)
        m = idl.getMethod(method_name)
        if m:
            info = m.getParameterInfos()[param_index]
            return info.aType.getName() == param_type
    except:
        pass
    return False


class Switcher(XJobExecutor, XServiceInfo, unohelper.Base):
    # Not used

    IMPLE_NAME = "___lo_identifier___.Switcher"
    SERVICE_NAMES = (IMPLE_NAME,)

    @staticmethod
    def get_imple(clazz):
        return clazz, clazz.IMPLE_NAME, clazz.SERVICE_NAMES

    def __init__(self, ctx, *args):
        XJobExecutor.__init__(self)
        XServiceInfo.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx

    def trigger(self, arg):
        desktop = create_service(self.ctx, "com.sun.star.frame.Desktop")
        doc = desktop.getCurrentComponent()
        layoutmgr = doc.getCurrentController().getFrame().LayoutManager

        if layoutmgr.isElementVisible(RESOURCE_URL):
            layoutmgr.hideElement(RESOURCE_URL)
        else:
            layoutmgr.requestElement(RESOURCE_URL)

    # XServiceInfo
    def supportedServiceNames(self):
        return self.SERVICE_NAMES

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getImplementationName(self):
        return self.IMPLE_NAME


# g_ImplementationHelper.addImplementation(*Switcher.get_imple())

"""
' Switch through layout manager.
const RESOURCE_URL = "private:resource/dockingwindow/___float_dialog_error_num___"

Sub SwitchDockingWindow
    layoutmgr = ThisComponent.getCurrentController().getFrame().LayoutManager
    if layoutmgr.isElementVisible(RESOURCE_URL) then
        layoutmgr.hideElement(RESOURCE_URL)
    else
        layoutmgr.requestElement(RESOURCE_URL)
    end if
End Sub
"""

"""
' Way to show/hide docking window through dispatch framework.
Sub ShowDockingWindow()
    id = 9809
    a = "DockingWindow" & CStr(id - 9800)
    p = CreateUnoStruct("com.sun.star.beans.PropertyValue")
    p.Name = a
    p.Value = True ' show or hide(False)

    dp = CreateUnoService("com.sun.star.frame.DispatchHelper")
    dp.executeDispatch(ThisComponent.getCurrentController().getFrame(), _
        ".uno:" & a, "_self", 0, Array(p))

End Sub
"""
