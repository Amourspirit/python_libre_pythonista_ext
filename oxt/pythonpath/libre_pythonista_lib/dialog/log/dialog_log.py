from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
import contextlib
import os

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
import unohelper

from com.sun.star.awt import KeyModifier
from com.sun.star.awt import Rectangle
from com.sun.star.awt import VclWindowPeerAttribute
from com.sun.star.awt import WindowAttribute
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt import XMenuBar
from com.sun.star.awt import XTopWindowListener
from com.sun.star.awt.WindowClass import TOP
from com.sun.star.frame import XFrame
from com.sun.star.beans import NamedValue
from com.sun.star.lang import XSingleServiceFactory
from ooo.dyn.awt.font_descriptor import FontDescriptor
from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.awt.size import Size
from ooo.dyn.style.vertical_alignment import VerticalAlignment


from ooodev.dialog import BorderKind
from ooodev.dialog.dl_control import CtlTextEdit
from ooodev.dialog.msgbox import MsgBox, MessageBoxResultsEnum, MessageBoxType, MessageBoxButtonsEnum
from ooodev.events.args.event_args import EventArgs
from ooodev.events.lo_events import LoEvents
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.loader import Lo
from ooodev.utils.color import StandardColor
from ooodev.utils.partial.the_dictionary_partial import TheDictionaryPartial
from ooodev.utils.sys_info import SysInfo


if TYPE_CHECKING:
    from com.sun.star.awt import MenuBar  # service
    from com.sun.star.awt import MenuEvent  # struct
    from com.sun.star.lang import EventObject  # struct
    from com.sun.star.frame import TaskCreator  # service
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ..window_type import WindowType
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.lo_util.resource_resolver import ResourceResolver

    from ...dialog.options.log_opt import LogOpt
    from ...config.dialog.log_cfg import LogCfg
    from ...const.event_const import GBL_DOC_CLOSING, LOG_PY_LOGGER_RESET
    from ...event.shared_event import SharedEvent
    from ...log.py_logger import PyLogger
    from .dialog_log_menu import DialogLogMenu
    from .dialog_log_window_listener import DialogLogWindowListener
    from .key_handler import KeyHandler

    # from com.sun.star.frame import TaskCreator  # service
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from libre_pythonista_lib.dialog.options.log_opt import LogOpt
    from libre_pythonista_lib.config.dialog.log_cfg import LogCfg
    from libre_pythonista_lib.const.event_const import GBL_DOC_CLOSING, LOG_PY_LOGGER_RESET
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.py_logger import PyLogger
    from libre_pythonista_lib.dialog.log.dialog_log_menu import DialogLogMenu
    from libre_pythonista_lib.dialog.log.dialog_log_window_listener import DialogLogWindowListener
    from libre_pythonista_lib.dialog.log.key_handler import KeyHandler

# see Also: https://ask.libreoffice.org/t/top-window-crashes-when-a-menubar-is-added/107282 This is not a issue here.


class DialogLog(TheDictionaryPartial, XTopWindowListener, unohelper.Base):
    _instances: Dict[str, DialogLog] = {}

    IS_WINDOWS = os.name == "nt"
    FONT = "DejaVu Sans Mono"
    MARGIN = 3
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 26
    WIDTH = 600
    NB_TAB = 4
    HEADER = 1  # can create space for label at the top
    FOOTER = 0
    if IS_WINDOWS:
        FOOTER += 24
    HEIGHT = 310
    MIN_HEIGHT = HEADER + FOOTER + 30
    MIN_WIDTH = 225

    def __new__(cls, ctx: Any) -> DialogLog:  # noqa: ANN401
        assert Lo.current_doc is not None
        uid = Lo.current_doc.runtime_uid
        key = f"doc_{uid}"
        if key not in cls._instances:
            inst = super(DialogLog, cls).__new__(cls)
            inst._is_init = False
            inst.runtime_uid = uid
            inst.__init__(ctx)
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        if getattr(self, "_is_init", False):
            return
        TheDictionaryPartial.__init__(self)
        XTopWindowListener.__init__(self)
        unohelper.Base.__init__(self)
        assert Lo.current_doc is not None
        self.runtime_uid: str
        self._platform = SysInfo.get_platform()
        self._ctx = ctx
        self._is_visible = True
        self._closing_triggered = False
        self._config_updated = False
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init")
        self._cfg = LogCfg()
        self._rr = ResourceResolver(Lo.get_context())
        self._doc = Lo.current_doc
        self._disposed = False
        if self._cfg.has_size():
            self._log.debug("Config Has Size")
            self._width = self._cfg.width
            self._height = self._cfg.height
        else:
            self._log.debug("Config does not have Size. Using Defaults.")
            self._width = DialogLog.WIDTH
            self._height = DialogLog.HEIGHT
        self._code_border_color = StandardColor.TEAL_LIGHT2
        self._border_kind = BorderKind.BORDER_SIMPLE
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 10
        else:
            self._padding = 14
        self._current_tab_index = 1
        self._padding = 14
        self._btn_width = DialogLog.BUTTON_WIDTH
        self._btn_height = DialogLog.BUTTON_HEIGHT
        self._margin = DialogLog.MARGIN
        self._frame = None
        font = FontDescriptor()
        font.Name = DialogLog.FONT
        self._fd = font
        self._main_menu = None
        self.end = 0
        self.keyhandler = KeyHandler(self)
        self._title = self._rr.resolve_string("title12")  # Log Window

        self._mb = cast("MenuBar", None)
        try:
            self.parent = self.get_parent()
            self.tk = self.parent.Toolkit  # type: ignore
            self._init_handlers()
            self._init_dialog()
            self._add_frame()
            self._add_menu_bar()
            self._init_log_txt()
            self._dialog.addWindowListener(DialogLogWindowListener(self))
            self._dialog.addTopWindowListener(self)
            self._init_style()
            self._py_logger = PyLogger(doc=self._doc)
            self._share_event = SharedEvent(self._doc)  # type: ignore
            self._share_event.subscribe_event(LOG_PY_LOGGER_RESET, self._fn_on_log_py_inst_reset)
            PyLogger.reset_instance(doc=self._doc)
            self._is_init = True
            self._log.debug("Init Complete")
        except Exception as e:
            self._log.exception(f"Error in DialogLog.__init__:")

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        rect = Rectangle()
        rect.Width = self._width
        if self._cfg.has_size():
            rect.Height = self._height + self._cfg.menu_bar_height
        else:
            rect.Height = self._height

        if self._cfg.has_position():
            self._log.debug("_init_dialog() Config Has Position")
            rect.X = self._cfg.x
            rect.Y = max(0, self._cfg.y - self._cfg.menu_bar_height)
        else:
            ps = self.parent.getPosSize()  # type: ignore
            rect.X = int((ps.Width - self._width) / 2 - 50)
            rect.Y = int((ps.Height - self._height) / 2 - 100)

        desc = WindowDescriptor()
        desc.Type = TOP
        desc.WindowServiceName = "window"
        desc.ParentIndex = -1
        desc.Parent = None  # type: ignore
        desc.Bounds = rect
        desc.WindowAttributes = (
            WindowAttribute.SHOW
            | WindowAttribute.BORDER
            | WindowAttribute.CLOSEABLE
            | WindowAttribute.SIZEABLE
            | WindowAttribute.MOVEABLE
            # | VclWindowPeerAttribute.CLIPCHILDREN
        )

        dialog_peer = self.tk.createWindow(desc)
        try:
            dialog_peer.setTitle(self._title)
        except Exception:
            self._log.debug("Error setting dialog title")

        self._dialog = cast("WindowType", dialog_peer)
        if self._platform == SysInfo.PlatformEnum.MAC:
            self._dialog.setVisible(True)
        else:
            self._dialog.setVisible(False)
        self._dialog.setOutputSize(Size(rect.Width, rect.Height))

    def _init_handlers(self) -> None:
        self._fn_on_menu_select = self._on_menu_select
        self._fn_on_log_event = self._on_log_event
        self._fn_on_log_py_inst_reset = self._on_log_py_inst_reset

    def _init_style(self) -> None:
        # setting code border and border color seems to have no effect.
        self._log_txt.border = BorderKind.BORDER_3D
        self._log_txt.border_color = StandardColor.TEAL_LIGHT1

    def _add_frame(self) -> None:
        """Add frame to dialog"""
        # When using TaskCreator a window is automatically added to the frame
        # Also closing window must be implemented manually in the windowClosing event.
        tc = cast(
            "TaskCreator",
            Lo.create_instance_mcf(XSingleServiceFactory, "com.sun.star.frame.TaskCreator", raise_err=True),
        )
        rect = Rectangle()
        rect.Width = self._width
        rect.Height = self._height

        if self._cfg.has_position():
            self._log.debug("_init_dialog() Config Has Position")
            rect.X = self._cfg.x
            rect.Y = self._cfg.y
        else:
            ps = self.parent.getPosSize()  # type: ignore
            rect.X = int((ps.Width - self._width) / 2 - 50)
            rect.Y = int((ps.Height - self._height) / 2 - 100)

        frame = cast(
            XFrame,
            tc.createInstanceWithArguments(
                (NamedValue("FrameName", f"DialogLog_{self.runtime_uid}"), NamedValue("PosSize", rect))
            ),
        )
        try:
            frame.Title = self._title  # type: ignore
        except Exception:
            self._log.debug("Error setting frame title")

        frame.setComponent(self._dialog, None)  # type: ignore
        frame.setCreator(Lo.desktop.component)
        Lo.desktop.get_frames().append(frame)
        self._frame = frame

        # -- or --

        # frame = Lo.create_instance_mcf(XFrame, "com.sun.star.frame.Frame", raise_err=True)
        # frame.setName(f"DialogLog_{self.runtime_uid}")
        # frame.initialize(self._dialog)
        # try:
        #     frame.Title = self._title  # type: ignore
        # except Exception:
        #     self._log.debug("Error setting frame title")
        # self._frame = frame

    # region Misc Methods

    # region Controls
    def _init_log_txt(self) -> None:
        txt_y = DialogLog.HEADER + self._margin

        # txt_height = DialogLog.HEIGHT - DialogLog.FOOTER - (self._margin * 2) - txt_y
        txt_height = DialogLog.HEIGHT - DialogLog.FOOTER - txt_y
        self._log_txt = CtlTextEdit.create(
            self._dialog,
            x=self._margin,
            y=txt_y,
            width=self._width - (self._margin * 1),
            height=txt_height,
            Text="",
            Border=int(self._border_kind),
            BorderColor=self._code_border_color,
            VerticalAlign=VerticalAlignment.TOP,
            ReadOnly=False,
            MultiLine=True,
            AutoHScroll=True,
            AutoVScroll=True,
            HScroll=True,
            VScroll=True,
            FontDescriptor=self._fd,
            HideInactiveSelection=True,
            Tabstop=True,
        )
        # self._code.view.addTextListener(TextListener(self))
        # self._code.add_event_text_changed(self._fn_on_text_changed)  # type: ignore
        # # self._code.add_event_key_pressed(self._fn_on_code_key_pressed)  # type: ignore
        # self._code.add_event_focus_gained(self._fn_on_code_focus_gained)  # type: ignore
        # self._code.add_event_focus_lost(self._fn_on_code_focus_lost)  # type: ignore
        # self._code.view.setFocus()

    # endregion Controls

    def _set_tab_index(self, ctl: Any) -> None:  # noqa: ANN401
        ctl.tab_index = self._current_tab_index
        self._current_tab_index += 1

    def get_parent(self) -> Any:  # noqa: ANN401
        """Returns parent frame"""
        try:
            window = Lo.desktop.get_active_frame().getContainerWindow()
            if window is None:
                raise Exception("Window is None")
            return window
        except Exception:
            self._log.error("Error in get_parent", exc_info=True)
            return None

    # endregion Misc Methods

    # region Menubar
    def _add_menu_bar(self) -> None:
        try:
            menu_provider = DialogLogMenu(self)

            mb = Lo.create_instance_mcf(XMenuBar, "com.sun.star.awt.MenuBar", raise_err=True)
            mb.insertItem(1, self._rr.resolve_string("mnuFile"), 0, 0)
            mb.insertItem(2, self._rr.resolve_string("mnuView"), 0, 1)
            mb.insertItem(3, self._rr.resolve_string("mnuSettings"), 0, 2)
            file_mnu = menu_provider.get_file_menu()
            file_mnu.subscribe_all_item_selected(self._fn_on_menu_select)
            mb.setPopupMenu(1, file_mnu.component)  # type: ignore
            view_mnu = menu_provider.get_view_menu()
            view_mnu.subscribe_all_item_selected(self._fn_on_menu_select)
            mb.setPopupMenu(2, view_mnu.component)  # type: ignore

            setting_mnu = menu_provider.get_settings_menu()
            setting_mnu.subscribe_all_item_selected(self._fn_on_menu_select)
            mb.setPopupMenu(3, setting_mnu.component)  # type: ignore

            self._mb = mb
            self._dialog.setMenuBar(mb)
        except Exception as e:
            self._log.exception("Error adding menubar")

    # endregion Menubar

    # region Event Handlers
    def _on_menu_select(self, src: Any, event: EventArgs, menu: PopupMenu) -> None:  # noqa: ANN401
        self._log.debug("Menu Selected")
        me = cast("MenuEvent", event.event_data)
        command = menu.get_command(me.MenuId)
        self._log.debug(f"_on_menu_select() Menu Selected: {command}, Menu ID: {me.MenuId}")
        # self._write_line(f"Menu Selected: {command}, Menu ID: {me.MenuId}")

        try:
            if command == ".uno:lp.rest_data":
                result = MsgBox.msgbox(
                    title=self._rr.resolve_string("mbtitle006"),
                    msg=self._rr.resolve_string("mbmsg006"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if result == MessageBoxResultsEnum.YES:
                    self.clear()
                return
            elif command == ".uno:lp.close":
                self._log.debug("_on_menu_select() command Matched: .uno:lp.close")
                result = MsgBox.msgbox(
                    title=self._rr.resolve_string("mbtitle007"),
                    msg=self._rr.resolve_string("mbmsg007"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if result == MessageBoxResultsEnum.YES:
                    self._log.debug("_on_menu_select() Close Confirmed")
                    self._update_config()
                    self._log.debug("_on_menu_select() Disposing")
                    self.dispose()
                    self._log.debug("_on_menu_select() Disposed")
                else:
                    self._log.debug("Close Cancelled")
            elif command == ".uno:lp.hide_window":
                self.visible = False
            elif command == ".uno:lp.log_settings":
                LogOpt().show()
                return
        except Exception:
            self._log.exception("Error in _on_menu_select")
        return

    def _on_log_event(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        if self._log.is_debug:
            self._log.debug("_on_log_event, Writing Line")
        self._write_line(event.event_data.log_msg)

    def _on_log_py_inst_reset(self, src: Any, event_args: EventArgs) -> None:  # noqa: ANN401
        self._log.debug("_on_log_py_inst_reset")
        try:
            self._py_logger = PyLogger(doc=self._doc)
            self._py_logger.unsubscribe_log_event(self._fn_on_log_event)
            self._py_logger.subscribe_log_event(self._fn_on_log_event)
        except Exception:
            self._log.exception("_on_log_py_inst_reset")

    # endregion Event Handlers

    # region Window Methods
    def set_focus(self) -> None:
        self._dialog.setFocus()

    def _update_config(self) -> None:
        self._log.debug("Updating Window Config")
        if self._config_updated == True:
            return
        try:
            sz_pos = self._dialog.getPosSize()
            sz = self._dialog.getOutputSize()

            self._cfg.width = sz.Width
            self._cfg.height = sz.Height
            self._cfg.x = sz_pos.X
            self._cfg.y = sz_pos.Y
            self._cfg.menu_bar_height = 30  # add for the menu bar. Does not seem possible to get the real height.

            # get the menubar height and add it.
            self._cfg.save()
            self._config_updated = True
            self._log.debug("Config Updated")
        except Exception:
            self._log.exception("Error updating config")

    def close(self) -> None:
        self._log.debug("Window Closing")
        self._update_config()
        self.dispose()

    # endregion Window Methods

    # region Write Methods
    def clear(self) -> None:
        """Clears the Log Text."""
        self._log_txt.text = ""

    def _write_line(self, text: str) -> None:
        self._log_txt.write_line(text)

    def _clear_data(self) -> None:
        self._log.debug("_clear_data")
        try:
            self._py_logger = PyLogger(doc=self._doc)
            self._py_logger.unsubscribe_log_event(self._fn_on_log_event)
            self._py_logger.subscribe_log_event(self._fn_on_log_event)
        except Exception:
            self._log.exception("_clear_data")

    # endregion Write Methods

    # region Dialog Methods

    def show(self) -> None:
        if not self._dialog.isVisible():
            try:
                self._dialog.setVisible(True)
            except Exception:
                self._log.exception("Failed to set Window visible")
                raise
        if not self._dialog.hasFocus():
            self.set_focus()
        try:
            # it seems only macOs needs this
            self.resize()
        except Exception:
            self._log.exception("Failed to resize.")

    def dispose(self) -> None:
        self._log.debug("Dispose Called")
        try:
            self._is_visible = True  # make sure set flag to true so windowClosed can process.
            self._dialog.dispose()
            if self._frame is not None:
                Lo.desktop.get_frames().remove(self._frame)
                self._frame.dispose()
                self._frame = None
                self._log.debug("Frame Removed and Disposed.")
        except Exception as e:
            self._log.error("Error in disposing", exc_info=True)

    # endregion Dialog Methods

    # region resize
    def _resize_log_txt(self, sz: Rectangle) -> None:
        txt_sz = self._log_txt.view.getPosSize()
        width = sz.Width - (self._margin * 1)
        # txt_height = sz.Height - DialogLog.FOOTER - (self._margin * 2) - txt_sz.Y
        txt_height = sz.Height - DialogLog.FOOTER - txt_sz.Y
        self._log_txt.view.setPosSize(txt_sz.X, txt_sz.Y, width, txt_height, PosSize.POSSIZE)

    def resize(self) -> None:
        sz = self._dialog.getPosSize()
        if sz.Height < DialogLog.MIN_HEIGHT:
            return
        if sz.Width < DialogLog.MIN_WIDTH:
            return
        self._resize_log_txt(sz)

    # endregion resize

    # region Key Handlers
    def onkey_1282(self, modifiers: str) -> bool:  # TAB
        """Catch TAB keyboard entry"""
        if not modifiers:
            pass
        return False

    def onkey_526(self, modifiers: str) -> bool:  # o
        if modifiers == KeyModifier.SHIFT | KeyModifier.MOD1:
            pass
            # return True
        return False

    # endregion Key Handlers

    # region XTopWindowListener
    @override
    def windowOpened(self, e: EventObject) -> None:
        """is invoked when a window is activated."""
        self._log.debug("Window Opened")

    @override
    def windowActivated(self, e: EventObject) -> None:
        """is invoked when a window is activated."""

        self._log.debug("Window Activated")

    @override
    def windowDeactivated(self, e: EventObject) -> None:
        """is invoked when a window is deactivated."""
        self._log.debug("Window De-activated")

    @override
    def windowMinimized(self, e: EventObject) -> None:
        """Is invoked when a window is iconified."""
        self._log.debug("Window Minimized")

    @override
    def windowNormalized(self, e: EventObject) -> None:
        """is invoked when a window is deiconified."""
        self._log.debug("Window Normalized")

    @override
    def windowClosing(self, e: EventObject) -> None:
        """
        is invoked when a window is in the process of being closed.

        The close operation can be overridden at this point.
        """
        self._log.debug("Window Closing")
        result = MsgBox.msgbox(
            title=self._rr.resolve_string("mbtitle007"),
            msg=self._rr.resolve_string("mbmsg007"),
            boxtype=MessageBoxType.QUERYBOX,
            buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
        )
        if result != MessageBoxResultsEnum.YES:
            self._log.debug(f"windowClosing() Close Cancelled. Result: {result}")
            return
        self._log.debug("windowClosing() Close Confirmed")

        if not self._closing_triggered:
            self._closing_triggered = True
            try:
                self._update_config()
            except Exception as err:
                self._log.exception(f"Error saving configuration: {err}")
            self.dispose()

    @override
    def windowClosed(self, e: EventObject) -> None:
        """is invoked when a window has been closed."""
        if not self._is_visible:
            self._log.debug("windowClosed() Window is hidden, not terminating.")
            return
        self._log.debug("Window Closed")
        DialogLog.reset_inst(self.runtime_uid)

    @override
    def disposing(self, Source: EventObject) -> None:
        self._log.debug("Disposing")
        if not self._disposed:
            try:
                DialogLog.reset_inst(self.runtime_uid)
                self._disposed = True
                self._dialog.removeTopWindowListener(self)
                self._dialog.setMenuBar(None)  # type: ignore
                self._mb = None
                self._dialog.dispose()
            except Exception:
                self._log.error("Error in disposing", exc_info=True)

    # endregion XTopWindowListener

    # region Static Methods
    @classmethod
    def reset_inst(cls, uid: str = "") -> None:
        """Reset instance"""
        if not uid:
            for key in cls._instances:
                _close_dialog(key)
            cls._instances = {}
            return
        key = f"doc_{uid}"
        _close_dialog(key)

    @classmethod
    def has_instance(cls, uid: str) -> bool:
        """Gets if an instance already exists."""
        key = f"doc_{uid}"
        return key in cls._instances

    @classmethod
    def get_instance(cls, uid: str) -> DialogLog:
        """Gets the instance. Should check with has_instance first."""
        key = f"doc_{uid}"
        return cls._instances[key]

    # endregion Static Methods

    # region properties

    @property
    def res_resolver(self) -> ResourceResolver:
        """Gets the Resource Resolver object."""
        return self._rr

    @property
    def text(self) -> str:
        """Gets/Sets the text of the code edit control."""
        return self._log_txt.text

    @text.setter
    def text(self, value: str) -> None:
        self._log_txt.text = value

    @property
    def doc(self) -> OfficeDocumentT:
        """Gets the current document."""
        return self._doc

    @property
    def visible(self) -> bool:
        """Gets if the dialog is visible."""
        return self._dialog.isVisible()

    @visible.setter
    def visible(self, value: bool) -> None:
        self._is_visible = value
        self._dialog.setVisible(value)

    # endregion properties


def create_window_name(win_name: str) -> str:
    frames = Lo.desktop.get_frames()
    # frames = desktop.getFrames()

    count = 0
    for i in range(frames.getCount()):
        if frames.getByIndex(i).getName() == win_name:
            count = count + 1
    title = [win_name]
    while count > 0:
        title[0] = "%s - %s" % (win_name, (count + 1))
        for i in range(frames.getCount()):
            frame = frames.getByIndex(i)
            if frame.getName() == win_name and frame.getTitle() != title[0]:
                count = -2
                break
        count = count + 1
    return title[0]


def on_menu_select(src: Any, event: EventArgs, menu: PopupMenu) -> None:  # noqa: ANN401
    # print("Menu Selected")
    me = cast("MenuEvent", event.event_data)
    command = menu.get_command(me.MenuId)
    if command:  # noqa: SIM102
        # check if command is a dispatch command
        if menu.is_dispatch_cmd(command):
            menu.execute_cmd(command)


def _close_dialog(key: str) -> None:
    if key in DialogLog._instances:
        with contextlib.suppress(Exception):
            inst = DialogLog._instances[key]
            inst.dispose()
        with contextlib.suppress(Exception):
            # don't know why but sometimes a key error is raised.
            # This happened even thought the did call dispose above..
            del DialogLog._instances[key]


def _on_doc_closing(src: Any, event: EventArgs) -> None:  # noqa: ANN401
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"doc_{uid}"
    _close_dialog(key)


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
