from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple
import contextlib
from pathlib import Path
import sys
import uno
import unohelper
from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import XSingleComponentFactory


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    # this_pth = os.path.dirname(__file__)
    this_pth = str(Path(__file__).parent.parent.parent)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from ...___lo_pip___.oxt_logger import OxtLogger
    from com.sun.star.uno import XInterface
    from com.sun.star.uno import XComponentContext
    from com.sun.star.awt import UnoControlDialog  # service
    from ooodev.loader import Lo
    from ooodev.events.args.event_args import EventArgs
    from ooodev.dialog.msgbox import MessageBoxType, MsgBox
    from ...pythonpath.libre_pythonista_lib.dialog.handlers.log_win_handler import LogWinHandler
    from ...pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.const.event_const import DOCUMENT_FOCUS_GAINED, DOCUMENT_FOCUS_LOST
    from ...pythonpath.libre_pythonista_lib.const.res_const import RES_LOG_WIN_URL
else:
    from ___lo_pip___.oxt_logger import OxtLogger

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.dialog.msgbox import MessageBoxType, MsgBox
        from libre_pythonista_lib.dialog.handlers.log_win_handler import LogWinHandler
        from libre_pythonista_lib.log.log_inst import LogInst
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.const.event_const import DOCUMENT_FOCUS_GAINED, DOCUMENT_FOCUS_LOST
        from libre_pythonista_lib.const.res_const import RES_LOG_WIN_URL
    else:
        RES_LOG_WIN_URL = ""


# https://forum.openoffice.org/en/forum/viewtopic.php?p=295118


class DockingWindowFactoryImpl(XServiceInfo, XSingleComponentFactory, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.DockingWindowFactory"
    SERVICE_NAMES = (IMPLE_NAME,)

    def __init__(self, ctx, *args):
        global _CONDITIONS_MET
        XServiceInfo.__init__(self)
        XSingleComponentFactory.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        if _CONDITIONS_MET:
            self._log.debug("Conditions are met. Subscribing to focus events.")
            self._fn_on_focus_gained = self._on_focus_gained
            self._fn_on_focus_lost = self._on_focus_lost
            doc = Lo.current_doc
            self._se = SharedEvent(doc)
            self._se.subscribe_event(DOCUMENT_FOCUS_GAINED, self._fn_on_focus_gained)
            self._se.subscribe_event(DOCUMENT_FOCUS_LOST, self._fn_on_focus_lost)
        else:
            self._log.debug("Conditions not met")

    def _on_focus_gained(self, src: Any, event: EventArgs):
        self._log.debug(f"Focus gained for {event.event_data.run_id}")

    def _on_focus_lost(self, src: Any, event: EventArgs):
        self._log.debug(f"Focus Lost for {event.event_data.run_id}")

    def _display_error(self, msg: str):
        """Display error message."""
        global _CONDITIONS_MET
        if not _CONDITIONS_MET:
            return
        _ = MsgBox.msgbox(msg=msg, title="Error", boxtype=MessageBoxType.ERRORBOX)

    # region XSingleComponentFactory

    def createInstanceWithArgumentsAndContext(self, args: Tuple[Any, ...], ctx: XComponentContext) -> XInterface:
        """
        Creates an instance of a component and initializes the new instance with the given arguments and context.

        Raises:
            com.sun.star.uno.Exception: ``Exception``
        """
        try:
            self._log.debug(f"Creating instance Log Docking window")
            # desktop = create_service(ctx, "com.sun.star.frame.Desktop")
            # doc = desktop.getCurrentComponent()
            # key = f"doc_{doc.RuntimeUID}"
            # self._log.debug(f"Key: {key}")
            return create_window(ctx, args)
        except Exception as e:
            self._log.exception("createInstanceWithArgumentsAndContext() Error creating instance")
            # self._display_error(f"Error creating instance:\n{e}")

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
from com.sun.star.awt import XWindowListener
from com.sun.star.awt import PosSize
from com.sun.star.awt import VclWindowPeerAttribute
from com.sun.star.awt import WindowAttribute
from com.sun.star.awt.WindowClass import SIMPLE
from com.sun.star.task import XJobExecutor


# Valid resource URL for docking window starts with
# private:resource/dockingwindow. And valid name for them are
# 9800 - 9809 (only 10 docking windows can be created).
# See lcl_checkDockingWindowID function defined in
# source/sfx2/source/dialog/dockwin.cxx.
# If the name of dockingwindow conflict with other windows provided by
# other extensions, strange result would be happen.
# https://github.com/LibreOffice/core/blob/3c91fb758a429f51b89dfe9cea088691ced6d0c1/sfx2/source/dialog/dockwin.cxx#L292


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
            if arg.Value != RES_LOG_WIN_URL:
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
            WindowAttribute.SHOW
            | WindowAttribute.SIZEABLE
            | WindowAttribute.MOVEABLE
            | WindowAttribute.CLOSEABLE
            | VclWindowPeerAttribute.CLIPCHILDREN,
        )
        window = toolkit.createWindow(desc)

        # Create inner window from dialog
        dp = create("com.sun.star.awt.ContainerWindowProvider")
        child = cast("UnoControlDialog", dp.createContainerWindow(dialog1, "", window, None))
        if not _CONDITIONS_MET:
            child.setVisible(True)
            return window

        # need to listen to window here.
        # If the focus changes then also need to switch the switched to log handler for that specif window
        # log = LogInst()
        # if log.is_debug:
        #     log.debug(dir(window))
        handler = LogWinHandler(ctx, child)
        child.setVisible(True)
        # child.setPosSize(0, 0, 0, 0, PosSize.POS)  # if the dialog is not placed at
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
            self.handler.dialog.setPosSize(0, 0, ev.Width, ev.Height, PosSize.SIZE)
            self.handler.resize(ev.Width, ev.Height)
            # ToDo: resize dialog elements


# Tool functions


def create_service(ctx, name: str, args: Any = None) -> Any:
    """Create service with args if required."""
    smgr = ctx.getServiceManager()
    if args:
        return smgr.createInstanceWithArgumentsAndContext(name, args, ctx)
    else:
        return smgr.createInstanceWithContext(name, ctx)


class Switcher(XJobExecutor, XServiceInfo, unohelper.Base):

    IMPLE_NAME = "___lo_identifier___.Switcher"
    SERVICE_NAMES = (IMPLE_NAME,)

    @classmethod
    def get_imple(cls):
        return cls, cls.IMPLE_NAME, cls.SERVICE_NAMES

    def __init__(self, ctx, *args):
        XJobExecutor.__init__(self)
        XServiceInfo.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx

    def trigger(self, arg):
        global RES_LOG_WIN_URL
        desktop = create_service(self.ctx, "com.sun.star.frame.Desktop")
        doc = desktop.getCurrentComponent()
        layoutmgr = doc.getCurrentController().getFrame().LayoutManager

        if layoutmgr.isElementVisible(RES_LOG_WIN_URL):
            layoutmgr.hideElement(RES_LOG_WIN_URL)
        else:
            layoutmgr.requestElement(RES_LOG_WIN_URL)

    # XServiceInfo
    def supportedServiceNames(self):
        return self.SERVICE_NAMES

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getImplementationName(self):
        return self.IMPLE_NAME


g_ImplementationHelper.addImplementation(*Switcher.get_imple())


class LogViewLoader(XJobExecutor, XServiceInfo, unohelper.Base):
    # https://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1frame_1_1XLayoutManager.html
    IMPLE_NAME = "___lo_identifier___.LogViewLoader"
    SERVICE_NAMES = (IMPLE_NAME,)

    @classmethod
    def get_imple(cls):
        return cls, cls.IMPLE_NAME, cls.SERVICE_NAMES

    def __init__(self, ctx, *args):
        XJobExecutor.__init__(self)
        XServiceInfo.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx

    def trigger(self, arg):
        global RES_LOG_WIN_URL
        desktop = create_service(self.ctx, "com.sun.star.frame.Desktop")
        doc = desktop.getCurrentComponent()
        if doc is None:
            return
        layoutmgr = doc.getCurrentController().getFrame().LayoutManager

        if layoutmgr.isElementVisible(RES_LOG_WIN_URL):
            # layoutmgr.destroyElement(RESOURCE_URL)
            # layoutmgr.createElement(RESOURCE_URL)
            layoutmgr.hideElement(RES_LOG_WIN_URL)
            layoutmgr.requestElement(RES_LOG_WIN_URL)
        # else:
        #     layoutmgr.requestElement(RESOURCE_URL)

    # XServiceInfo
    def supportedServiceNames(self):
        return self.SERVICE_NAMES

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getImplementationName(self):
        return self.IMPLE_NAME


g_ImplementationHelper.addImplementation(*LogViewLoader.get_imple())


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
