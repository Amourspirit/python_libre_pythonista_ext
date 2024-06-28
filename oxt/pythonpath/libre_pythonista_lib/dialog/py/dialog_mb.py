from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple
import time
from threading import Thread

import uno
import unohelper

from com.sun.star.awt import KeyModifier
from com.sun.star.awt import MenuItemStyle
from com.sun.star.awt import Rectangle
from com.sun.star.awt import Selection
from com.sun.star.awt import VclWindowPeerAttribute
from com.sun.star.awt import WindowAttribute
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt import XMenuBar
from com.sun.star.awt import XTopWindowListener
from com.sun.star.awt.WindowClass import TOP
from com.sun.star.beans import NamedValue
from com.sun.star.frame import XFrame
from com.sun.star.lang import XSingleServiceFactory
from ooo.dyn.awt.font_descriptor import FontDescriptor
from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.style.vertical_alignment import VerticalAlignment

from ooodev.dialog import BorderKind
from ooodev.dialog.dl_control import CtlButton, CtlTextEdit, CtlFixedText
from ooodev.dialog.msgbox import MessageBoxResultsEnum, MessageBoxType
from ooodev.events.args.event_args import EventArgs
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.globals import GblEvents
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator
from ooodev.loader import Lo
from ooodev.loader.inst.doc_type import DocType
from ooodev.utils.partial.the_dictionary_partial import TheDictionaryPartial

from ...const import UNO_DISPATCH_PY_CODE_VALIDATE, UNO_DISPATCH_SEL_RNG
from .dialog_mb_window_listener import DialogMbWindowListener
from .key_handler import KeyHandler
from ...config.dialog.code_cfg import CodeCfg
from .top_listener_rng import TopListenerRng
from .dialog_mb_menu import DialogMbMenu

if TYPE_CHECKING:
    from com.sun.star.awt import MenuBar  # service
    from com.sun.star.awt import MenuEvent  # struct
    from com.sun.star.lang import EventObject  # struct
    from com.sun.star.frame import TaskCreator  # service
    from com.sun.star.accessibility import XAccessibleComponent
    from ooodev.calc import CalcDoc
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ..window_type import WindowType
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver

# see Also: https://ask.libreoffice.org/t/top-window-crashes-when-a-menubar-is-added/107282 This is not a issue here.


class DialogMb(TheDictionaryPartial, EventsPartial, XTopWindowListener, unohelper.Base):
    _instances = {}

    FONT = "DejaVu Sans Mono"
    MARGIN = 3
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 26
    WIDTH = 600
    NB_TAB = 4
    HEADER = 10  # can create space for label at the top
    FOOTER = 40
    HEIGHT = 310
    MIN_HEIGHT = HEADER + FOOTER + 30
    MIN_WIDTH = 225

    def __new__(cls, ctx: Any, inst_id: str):
        if inst_id not in cls._instances:
            cls._instances[inst_id] = super(DialogMb, cls).__new__(cls)
            cls._instances[inst_id]._is_init = False
        return cls._instances[inst_id]

    def __init__(self, ctx: Any, inst_id: str) -> None:
        if getattr(self, "_is_init", True):
            return
        TheDictionaryPartial.__init__(self)
        EventsPartial.__init__(self)
        XTopWindowListener.__init__(self)
        unohelper.Base.__init__(self)
        self._dialog_result = MessageBoxResultsEnum.CANCEL
        self._is_shown = False
        self._closing_triggered = False
        self._config_updated = False
        self._inst_id = inst_id
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init")
        self._cfg = CodeCfg()
        self._rr = ResourceResolver(Lo.get_context())
        self._doc = Lo.current_doc
        self._disposed = False
        if self._cfg.has_size():
            self._log.debug("Config Has Size")
            self._width = self._cfg.width
            self._height = self._cfg.height
        else:
            self._log.debug("Config does not have Size. Using Defaults.")
            self._width = DialogMb.WIDTH
            self._height = DialogMb.HEIGHT
        self._border_kind = BorderKind.BORDER_3D
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 10
        else:
            self._padding = 14
        self._current_tab_index = 1
        self._padding = 14
        self._btn_width = DialogMb.BUTTON_WIDTH
        self._btn_height = DialogMb.BUTTON_HEIGHT
        self._margin = DialogMb.MARGIN
        self._frame = None
        font = FontDescriptor()
        font.Name = DialogMb.FONT
        self._fd = font
        self._main_menu = None
        self.end = 0
        self.keyhandler = KeyHandler(self)
        self._title = self._rr.resolve_string("title10")

        self._mb = cast("MenuBar", None)
        try:
            self.parent = self.get_parent()
            self.tk = self.parent.Toolkit  # type: ignore
            self._init_handlers()
            self._init_dialog()
            self._add_frame()
            self._add_menu_bar()
            self._init_buttons()
            self._init_code()
            self._init_info_label()
            self._dialog.addWindowListener(DialogMbWindowListener(self))
            self._dialog.addTopWindowListener(self)
            self._init_style()
            self._log.debug("Init Complete")
            self._is_init = True
        except Exception as e:
            self._log.exception(f"Error in DialogMb.__init__:")

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
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

        desc = WindowDescriptor()
        desc.Type = TOP
        desc.WindowServiceName = "window"
        desc.ParentIndex = -1
        desc.Parent = None  # type: ignore
        desc.Bounds = rect

        desc.WindowAttributes = (
            # WindowAttribute.SHOW
            WindowAttribute.BORDER
            + WindowAttribute.SIZEABLE
            + WindowAttribute.MOVEABLE
            + VclWindowPeerAttribute.CLIPCHILDREN
        )

        dialog_peer = self.tk.createWindow(desc)

        self._dialog = cast("WindowType", dialog_peer)
        self._dialog.setVisible(False)
        # self._dialog.setBackground(get_bg_color(self._dialog, 0xFAFAFA))

    def _init_style(self) -> None:
        if self._mb is not None:
            self._dialog.setBackground(get_bg_color(self._mb, 0xFAFAFA))  # type: ignore

    # region Misc Methods

    def _set_tab_index(self, ctl: Any) -> None:
        ctl.tab_index = self._current_tab_index
        self._current_tab_index += 1

    def get_parent(self):
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

    def _init_handlers(self) -> None:
        """
        Add event handlers for when changes occur.

        Methods can not be assigned directly to control callbacks.
        This is a python thing. However, methods can be assigned to class
        variable an in turn those can be assigned to callbacks.

        Example:
            ``self._ctl_btn_info.add_event_action_performed(self.on_button_action_preformed)``
            This would not work!

            ``self._ctl_btn_info.add_event_action_performed(self._fn_button_action_preformed)``
            This will work.
        """
        self._fn_on_text_changed = self.on_text_changed
        self._fn_on_code_key_pressed = self.on_code_key_pressed
        self._fn_on_code_focus_gained = self.on_code_focus_gained
        self._fn_on_code_focus_lost = self.on_code_focus_lost
        self._fn_on_btn_ok_click = self.on_btn_ok_click
        self._fn_on_btn_cancel_click = self.on_btn_cancel_click
        self._fn_on_menu_select = self._on_menu_select
        self._fn_on_menu_range_select_result = self._on_menu_range_select_result

    def _add_frame(self) -> None:
        """Add frame to dialog"""
        # create new empty frame and set window on it
        tc = cast(
            "TaskCreator",
            Lo.create_instance_mcf(XSingleServiceFactory, "com.sun.star.frame.TaskCreator", raise_err=True),
        )
        rect = Rectangle()
        rect.Width = self._width
        rect.Height = self._height

        # rect.X = 100
        # rect.Y = 100

        ps = self.parent.getPosSize()  # type: ignore
        rect.X = int((ps.Width - self._width) / 2 - 50)
        rect.Y = int((ps.Height - self._height) / 2 - 100)

        frame = cast(
            XFrame,
            tc.createInstanceWithArguments((NamedValue("FrameName", "DialogMb_Frame"), NamedValue("PosSize", rect))),
        )
        # frame = Lo.create_instance_mcf(XFrame, "com.sun.star.frame.Frame", raise_err=True)
        frame.setName("DialogMb_Frame")
        try:
            # Does not seem to do anything.
            # It depends from the type of the frame container window. If it is a system task window all will be OK.
            # https://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1frame_1_1XFrame2.html#aa7b633091e7820b835d04d0d5fc197c7
            frame.Title = self._title  # type: ignore
        except Exception:
            self._log.exception("Error setting title")
        # frame.setTitle(create_window_name(self._title))
        # frame.initialize(self._dialog)
        # The following block the menu events. Does not seem to be needed.
        frame.setComponent(self._dialog, None)  # type: ignore
        frame.setCreator(Lo.desktop.component)
        Lo.desktop.get_frames().append(frame)

        self._frame = frame

    # region XTopWindowListener
    def windowOpened(self, event: EventObject) -> None:
        """is invoked when a window is activated."""
        self._log.debug("Window Opened")

    def windowActivated(self, event: EventObject) -> None:
        """is invoked when a window is activated."""

        self._log.debug("Window Activated")

    def windowDeactivated(self, event: EventObject) -> None:
        """is invoked when a window is deactivated."""
        self._log.debug("Window De-activated")

    def windowMinimized(self, event: EventObject) -> None:
        """Is invoked when a window is iconified."""
        self._log.debug("Window Minimized")

    def windowNormalized(self, event: EventObject) -> None:
        """is invoked when a window is deiconified."""
        self._log.debug("Window Normalized")

    def windowClosing(self, event: EventObject) -> None:
        """
        is invoked when a window is in the process of being closed.

        The close operation can be overridden at this point.
        """
        self._log.debug("Window Closing")
        self._is_shown = False

        if not self._closing_triggered:
            self._closing_triggered = True
            try:
                self._update_config()
            except Exception as e:
                self._log.exception(f"Error saving configuration: {e}")

    def windowClosed(self, event: EventObject) -> None:
        """is invoked when a window has been closed."""
        self._log.debug("Window Closed")
        DialogMb.reset_inst(self._inst_id)

    def disposing(self, event: EventObject) -> None:

        print("Disposing")
        if not self._disposed:
            try:
                DialogMb.reset_inst(self._inst_id)
                self._is_shown = False
                self._disposed = True
                self._dialog.removeTopWindowListener(self)
                self._dialog.setMenuBar(None)  # type: ignore
                self._mb = None
                self._dialog.dispose()
            except Exception as e:
                self._log.error("Error in disposing", exc_info=True)

    # endregion XTopWindowListener

    # region Menubar
    def _add_menu_bar(self) -> None:
        try:
            menu_provider = DialogMbMenu(self)

            mb = Lo.create_instance_mcf(XMenuBar, "com.sun.star.awt.MenuBar", raise_err=True)
            mb.insertItem(1, self._rr.resolve_string("mnuCode"), 0, 0)
            mb.insertItem(2, self._rr.resolve_string("mnuInsert"), 0, 1)
            # mb.insertItem(2, "~Code", MenuItemStyle.AUTOCHECK, 1)
            insert_mnu = menu_provider.get_insert_menu()
            insert_mnu.subscribe_all_item_selected(self._fn_on_menu_select)
            code_mnu = menu_provider.get_code_menu()
            code_mnu.subscribe_all_item_selected(self._fn_on_menu_select)
            mb.setPopupMenu(1, code_mnu.component)  # type: ignore
            mb.setPopupMenu(2, insert_mnu.component)  # type: ignore
            self._mb = mb
            self._dialog.setMenuBar(mb)
        except Exception as e:
            self._log.exception("Error adding menubar")

    # endregion Menubar

    # region Controls
    def _init_buttons(self) -> None:
        """Add OK, Cancel and Info buttons to dialog control"""
        sz = self._dialog.getPosSize()

        btn_y = sz.Height - DialogMb.BUTTON_HEIGHT - self._padding  # - DialogMb.HEADER
        btn_x = sz.Width - DialogMb.BUTTON_WIDTH - self._padding

        self._ctl_btn_cancel = CtlButton.create(
            self._dialog,
            x=btn_x,
            y=btn_y,
            width=DialogMb.BUTTON_WIDTH,
            height=DialogMb.BUTTON_HEIGHT,
            Label=self._rr.resolve_string("dlg02"),
        )
        self._set_tab_index(self._ctl_btn_cancel)
        sz = self._ctl_btn_cancel.view.getPosSize()
        self._ctl_btn_ok = CtlButton.create(
            self._dialog,
            x=sz.X - sz.Width - self._margin,
            y=sz.Y,
            width=self._btn_width,
            height=self._btn_height,
            Label=self._rr.resolve_string("dlg01"),
            DefaultButton=True,
        )
        self._set_tab_index(self._ctl_btn_ok)
        self._ctl_btn_ok.add_event_action_performed(self._fn_on_btn_ok_click)  # type: ignore
        self._ctl_btn_cancel.add_event_action_performed(self._fn_on_btn_cancel_click)  # type: ignore

    def _init_code(self) -> None:
        txt_y = DialogMb.HEADER + self._margin

        txt_height = DialogMb.HEIGHT - DialogMb.FOOTER - (self._margin * 2) - txt_y  # - DialogMb.HEADER
        self._code = CtlTextEdit.create(
            self._dialog,
            x=self._margin,
            y=txt_y,
            width=self._width - (self._margin * 2),
            height=txt_height,
            Text="",
            Border=int(self._border_kind),
            VerticalAlign=VerticalAlignment.TOP,
            ReadOnly=False,
            MultiLine=True,
            AutoVScroll=True,
            FontDescriptor=self._fd,
            HideInactiveSelection=True,
            Tabstop=True,
        )
        # self._code.view.addTextListener(TextListener(self))
        self._code.add_event_text_changed(self._fn_on_text_changed)  # type: ignore
        # self._code.add_event_key_pressed(self._fn_on_code_key_pressed)  # type: ignore
        self._code.add_event_focus_gained(self._fn_on_code_focus_gained)  # type: ignore
        self._code.add_event_focus_lost(self._fn_on_code_focus_lost)  # type: ignore
        self._code.view.setFocus()

    def _init_info_label(self) -> None:
        """Add a fixed text label to the dialog control"""
        btn_sz = self._ctl_btn_cancel.view.getPosSize()
        lbl_width = btn_sz.X - (self._margin * 2)

        self._info_lbl_item = CtlFixedText.create(
            self._dialog,
            Label="",
            x=self._margin,
            y=btn_sz.Y,
            width=lbl_width,
            height=DialogMb.BUTTON_HEIGHT,
        )

    # endregion Controls

    # region resize
    def resize_buttons(self, sz: Rectangle) -> None:

        btn_y = sz.Height - DialogMb.BUTTON_HEIGHT - self._padding  # - DialogMb.HEADER
        btn_x = sz.Width - DialogMb.BUTTON_WIDTH - self._padding
        self._ctl_btn_cancel.view.setPosSize(
            btn_x, btn_y, DialogMb.BUTTON_WIDTH, DialogMb.BUTTON_HEIGHT, PosSize.POSSIZE
        )

        x = btn_x - DialogMb.BUTTON_WIDTH - self._margin
        self._ctl_btn_ok.view.setPosSize(x, btn_y, DialogMb.BUTTON_WIDTH, DialogMb.BUTTON_HEIGHT, PosSize.POSSIZE)

    def resize_code(self, sz: Rectangle) -> None:
        txt_sz = self._code.view.getPosSize()
        width = sz.Width - (self._margin * 2)
        txt_height = sz.Height - DialogMb.FOOTER - (self._margin * 2) - txt_sz.Y  # - DialogMb.HEADER
        self._code.view.setPosSize(txt_sz.X, txt_sz.Y, width, txt_height, PosSize.POSSIZE)

    def resize_info_lbl(self, sz: Rectangle) -> None:
        btn_sz = self._ctl_btn_cancel.view.getPosSize()
        lbl_width = btn_sz.X - (self._margin * 2)
        self._info_lbl_item.view.setPosSize(self._margin, btn_sz.Y, lbl_width, DialogMb.BUTTON_HEIGHT, PosSize.POSSIZE)

    def resize(self) -> None:
        sz = self._dialog.getPosSize()
        if sz.Height < DialogMb.MIN_HEIGHT:
            return
        if sz.Width < DialogMb.MIN_WIDTH:
            return
        self.resize_buttons(sz)
        self.resize_code(sz)
        self.resize_info_lbl(sz)

    # endregion resize

    # region button handlers
    def on_btn_ok_click(self, source: Any, event: EventArgs, control_src: CtlButton) -> None:
        eargs = EventArgs(self)
        dd = DotDict(text=self.text, doc=self._doc, inst_id=self._inst_id)
        dd.update(self.extra_data.copy())
        eargs.event_data = dd
        self.trigger_event("dialog_mb_ok", eargs)
        self._update_config()
        self._dialog_result = MessageBoxResultsEnum.OK
        self._is_shown = False

    def on_btn_cancel_click(self, source: Any, event: EventArgs, control_src: CtlButton) -> None:
        self._update_config()
        self._dialog_result = MessageBoxResultsEnum.CANCEL
        self._is_shown = False

    # endregion button handlers

    # region text_changed

    def on_text_changed(self, source: Any, event: EventArgs, control_src: CtlTextEdit) -> None:
        """Handle text changed event"""
        self.end = len(control_src.text)
        return
        self._log.debug(f"Text Changed {self.end}")
        sel = control_src.view.getSelection()
        self._log.debug("Selection: {sel.Min}, {sel.Max}")

    # endregion text_changed

    # region key handlers

    def on_code_key_pressed(self, source: Any, event: EventArgs, control_src: CtlTextEdit) -> None:
        pass
        # key_event = cast("KeyEvent", event.event_data)
        # if not key_event.Modifiers:
        #     self._write(" " * DialogPython.NB_TAB)

    # endregion key handlers

    # region focus handlers
    def on_code_focus_gained(self, source: Any, event: EventArgs, control_src: CtlTextEdit) -> None:
        self.code_focused = True
        self.tk.addKeyHandler(self.keyhandler)
        self._log.debug("Focus Gained")

    def on_code_focus_lost(self, source: Any, event: EventArgs, control_src: CtlTextEdit) -> None:
        self.code_focused = False
        self.tk.removeKeyHandler(self.keyhandler)
        self._log.debug("Focus Lost")

    # endregion focus handlers

    # region menu
    def _on_menu_select(self, src: Any, event: EventArgs, menu: PopupMenu) -> None:
        self._log.debug("Menu Selected")
        me = cast("MenuEvent", event.event_data)
        command = menu.get_command(me.MenuId)
        # self._write_line(f"Menu Selected: {command}, Menu ID: {me.MenuId}")

        if command == UNO_DISPATCH_PY_CODE_VALIDATE:
            try:
                self._doc.python_script.test_compile_python(self._code.text)
                title = self._rr.resolve_string("mbtitle001")
                msg = self._rr.resolve_string("mbmsg001")
                box_type = MessageBoxType.INFOBOX
            except Exception as e:
                title = self._rr.resolve_string("log09")  # error
                msg = str(e)
                box_type = MessageBoxType.ERRORBOX

            self._doc.msgbox(msg, title, box_type)
            return
        if self._doc.DOC_TYPE == DocType.CALC:
            if command == UNO_DISPATCH_SEL_RNG:
                self._dialog.setFocus()
                self._write_range_sel()
                # self._write_range_sel_popup(menu)
                return
        return

    def _on_menu_range_select_result(self, src: Any, event: EventArgs) -> None:
        log = self._log
        try:
            glbs = GblEvents()
            glbs.unsubscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_range_select_result)
        except:
            log.error("_on_menu_range_select_result() unsubscribing from GlobalCalcRangeSelector", exc_info=True)
        if event.event_data.state != "done":
            log.debug("on_sel _on_menu_range_select_result aborted")
            return
        log.debug(f"_on_menu_range_select_result {event.event_data.rng_obj}")
        try:
            view = event.event_data.view
            # doc = view.calc_doc
            # doc.msgbox(f"Selection made {event.event_data.rng_obj}")
            self._dialog.toFront()
            self._dialog.setFocus()

            sel = self._code.view.getSelection()
            # self._write(, (sel.Min, sel.Max))
            self._write(str(event.event_data.rng_obj), (sel.Min, sel.Max))
        except Exception:
            log.error("_on_menu_range_select_result", exc_info=True)

    # endregion menu

    # region Key Handlers
    def onkey_1282(self, modifiers: str) -> bool:  # TAB
        """Catch TAB keyboard entry"""
        if not modifiers:
            # self._log.debug("TAB")
            sel = self._code.view.getSelection()
            self._write(" " * DialogMb.NB_TAB, (sel.Min, sel.Max))
            return True
        return False

    def onkey_526(self, modifiers: str) -> bool:  # o
        if modifiers == KeyModifier.SHIFT | KeyModifier.MOD1:
            # self._write("ö")
            self._log.debug("Shift+Ctrl+o pressed")
            self._write_range_sel()
            return True
        else:
            self._log.debug(f"o pressed with modifiers {modifiers}")
        return False

    # endregion Key Handlers

    # region Code Edit
    def clear(self):
        """Clear edit area"""
        self._code.text = ""

    # region Read/Write

    def _write_range_sel(self) -> None:

        doc = cast("CalcDoc", self._doc)
        self._log.debug("_write_range_sel_popup() Write Range Selection Popup")
        try:
            glbs = GblEvents()
            glbs.subscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_range_select_result)
            self._log.debug("_write_range_sel_popup() Hide Dialog")
            doc.activate()
            _ = TopListenerRng(doc)
        except:
            self._log.error("_write_range_sel_popup() Error getting range selection", exc_info=True)
        finally:
            # For some reason this need to be here.
            # If not self._dialog.setFocus() the the top window listener will not fire right away.
            self._dialog.setFocus()

    def _write_line(self, text: str) -> None:
        self._code.write_line(text)

    def _write(self, data: str, sel: Tuple[int, int] | None = None):
        """Append data to edit control text"""
        if not sel:
            sel = (self.end, self.end)
        # sel = (0, 0)
        self._log.debug("Write", f'Data:"{data}"', "Selection", sel)
        self._code.view.insertText(Selection(*sel), data)

    # endregion Read/Write
    # endregion Code Edit

    # region Window Methods
    def set_focus(self):
        self._dialog.setFocus()

    def _update_config(self) -> None:
        self._log.debug("Updating Window Config")
        if self._config_updated == True:
            return
        try:
            sz = self._dialog.getPosSize()
            self._cfg.width = sz.Width
            self._cfg.height = sz.Height
            self._cfg.x = sz.X
            self._cfg.y = sz.Y
            self._cfg.save()
            self._config_updated = True
        except Exception:
            self._log.exception("Error updating config")

    # endregion Window Methods

    # region Dialog Methods

    def show(self) -> bool:
        self._is_shown = True
        self._dialog_result = MessageBoxResultsEnum.CANCEL
        self._dialog.setVisible(True)
        self.set_focus()
        # Start a new thread to wait for the dialog to close
        wait_thread = Thread(target=self._wait_for_hide)
        wait_thread.start()

        # Wait for the wait_thread to finish
        wait_thread.join()
        return self._dialog_result == MessageBoxResultsEnum.OK

    def _wait_for_hide(self):
        # Loop until the dialog is no longer visible
        while self._is_shown == True:
            time.sleep(0.1)  # Sleep to prevent high CPU usage

        # Perform any actions needed after the dialog is closed
        self._on_dialog_hidden()

    def _on_dialog_hidden(self):
        # Placeholder for any cleanup or actions needed after dialog closure
        self._dialog.setVisible(False)
        self._log.debug("Dialog Hidden")

    def dispose(self):
        self._log.debug("Dispose Called")
        try:
            self._dialog.dispose()
            if self._frame is not None:
                self._frame.dispose()
        except Exception as e:
            self._log.error("Error in disposing", exc_info=True)

    # endregion Dialog Methods

    # region Range Selection

    def _on_range_select_result(self, src: Any, event: EventArgs) -> None:
        log = self._log
        try:
            glbs = GblEvents()
            glbs.unsubscribe_event("GlobalCalcRangeSelector", self._fn_on_menu_range_select_result)
        except:
            log.error("_on_menu_range_select_result() unsubscribing from GlobalCalcRangeSelector", exc_info=True)
        if event.event_data.state != "done":
            log.debug("on_sel _on_menu_range_select_result aborted")
            return
        log.debug(f"_on_menu_range_select_result {event.event_data.rng_obj}")
        try:
            view = event.event_data.view
            self._dialog.toFront()
            self._dialog.setFocus()

            sel = self._code.view.getSelection()
            # self._write(, (sel.Min, sel.Max))
            self._write(str(event.event_data.rng_obj), (sel.Min, sel.Max))
        except Exception:
            log.error("_on_menu_range_select_result", exc_info=True)

    # endregion Range Selection

    # region Static Methods
    @classmethod
    def reset_inst(cls, inst_id: str = ""):
        """Reset instance"""
        if not inst_id:
            cls._instances = {}
        if inst_id in cls._instances:
            del cls._instances[inst_id]

    @classmethod
    def has_instance(cls, inst_id: str) -> bool:
        """Gets if an instance already exists."""
        return inst_id in cls._instances

    @classmethod
    def get_instance(cls, inst_id: str) -> DialogMb:
        """Gets the instance. Should check with has_instance first."""
        return cls._instances[inst_id]

    # endregion Static Methods

    # region properties

    @property
    def res_resolver(self) -> ResourceResolver:
        """Gets the Resource Resolver object."""
        return self._rr

    @property
    def text(self) -> str:
        """Gets/Sets the text of the code edit control."""
        return self._code.text

    @text.setter
    def text(self, value: str) -> None:
        self._code.text = value

    @property
    def info(self) -> str:
        return self._info_lbl_item.label

    @info.setter
    def info(self, value: str) -> None:
        self._info_lbl_item.label = value

    @property
    def doc(self) -> OfficeDocumentT:
        """Gets the current document."""
        return self._doc


def create_window_name(win_name: str):
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


def get_bg_color(comp: XAccessibleComponent, default: int = 0xEEEEEE) -> int:
    """Get background color through accessibility api."""
    import sys

    try:
        # acc = window.getAccessibleContext()
        # if sys.platform.startswith("win"):
        #     return acc.getAccessibleChild(0).getBackground()  # type: ignore
        # else:
        #     return acc.getBackground()  # type: ignore
        return comp.getBackground()
    except:
        pass
    return default


def on_menu_select(src: Any, event: EventArgs, menu: PopupMenu) -> None:
    print("Menu Selected")
    me = cast("MenuEvent", event.event_data)
    command = menu.get_command(me.MenuId)
    if command:
        # check if command is a dispatch command
        if menu.is_dispatch_cmd(command):
            menu.execute_cmd(command)
