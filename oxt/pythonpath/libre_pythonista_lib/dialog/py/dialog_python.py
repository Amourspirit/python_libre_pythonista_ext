# region Imports
from __future__ import annotations
import time
from typing import Any, cast, TYPE_CHECKING, Tuple
import uno
import unohelper
from com.sun.star.awt import XTopWindowListener
from com.sun.star.awt import Selection
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import TOP
from com.sun.star.awt import KeyModifier
from ooo.dyn.awt.window_attribute import WindowAttributeEnum
from ooo.dyn.awt.rectangle import Rectangle
from ooo.dyn.awt.font_descriptor import FontDescriptor
from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.style.vertical_alignment import VerticalAlignment
from ooodev.globals import GblEvents
from ooodev.dialog import BorderKind
from ooodev.dialog.msgbox import MessageBoxResultsEnum, MessageBoxType
from ooodev.loader import Lo
from ooodev.dialog.dl_control import CtlButton, CtlTextEdit, CtlFixedText
from ooodev.events.args.event_args import EventArgs
from ooodev.loader.inst.doc_type import DocType
from ooodev.utils.partial.the_dictionary_partial import TheDictionaryPartial

from ...const import UNO_DISPATCH_PY_CODE_VALIDATE, UNO_DISPATCH_SEL_RNG
from .window_listener import WindowListener
from .key_handler import KeyHandler

from .dialog_menu import DialogMenu
from ...config.dialog.code_cfg import CodeCfg
from .top_listener_rng import TopListenerRng


if TYPE_CHECKING:
    from com.sun.star.awt import MenuEvent
    from com.sun.star.lang import EventObject
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ooodev.calc import CalcDoc
    from ooodev.dialog.dl_control.ctl_base import DialogControlBase
    from ooodev.gui.menu.popup_menu import PopupMenu
    from ..window_type import WindowType
    from .....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

# endregion Imports


class DialogPython(TheDictionaryPartial, XTopWindowListener, unohelper.Base):
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

    # pylint: disable=unused-argument
    # region Init
    def __init__(self, ctx: Any) -> None:
        TheDictionaryPartial.__init__(self)
        XTopWindowListener.__init__(self)
        unohelper.Base.__init__(self)
        self._is_shown = True
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init")
        self._cfg = CodeCfg()
        self._rr = ResourceResolver(self.ctx)
        self._doc = Lo.current_doc
        self._doc.DOC_TYPE
        self._border_kind = BorderKind.BORDER_3D
        if self._cfg.has_size():
            self._log.debug("Config Has Size")
            self._width = self._cfg.width
            self._height = self._cfg.height
        else:
            self._log.debug("Config does not have Size. Using Defaults.")
            self._width = DialogPython.WIDTH
            self._height = DialogPython.HEIGHT
        self._btn_width = DialogPython.BUTTON_WIDTH
        self._btn_height = DialogPython.BUTTON_HEIGHT
        self._margin = DialogPython.MARGIN
        self._box_height = 30
        self._title = self._rr.resolve_string("title10")
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 10
        else:
            self._padding = 14
        self._current_tab_index = 1

        font = FontDescriptor()
        font.Name = DialogPython.FONT
        self._fd = font
        self._main_menu = None
        self.end = 0
        self._main_menu = None

        self.parent = self.get_parent()
        self.tk = self.parent.Toolkit  # type: ignore
        self.keyhandler = KeyHandler(self)
        self.code_focused = False
        self._mnu = DialogMenu(self)
        self._init_dialog()
        self._log.debug("Init Complete")

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        rect = Rectangle()
        rect.Width = self._width
        rect.Height = self._height
        # Although the x and y positions are correctly loading and saving from the configuration
        # the x and y are not being observed on all systems.
        # In the docker image the x and y work fine.
        # On the Flatpak and APT versions of LibreOffice, the x and y are not being observed
        # and the dialog is just show in the center of the app. This is not a big deal but I am noting it here.

        if self._cfg.has_position():
            self._log.debug("_init_dialog() Config Has Position")
            rect.X = self._cfg.x
            rect.Y = self._cfg.y
        else:
            ps = self.parent.getPosSize()
            rect.X = int((ps.Width - self._width) / 2 - 50)
            rect.Y = int((ps.Height - self._height) / 2 - 100)

        desc = WindowDescriptor()
        desc.Type = TOP
        desc.WindowServiceName = "dialog"
        desc.ParentIndex = -1
        desc.Bounds = rect

        # if WindowAttributeEnum.SHOW is set here, the dialog will not be sized on
        # some systems. The dialog would be displayed near full screen size.
        # This was the case for Flatpak and APT versions on Ubuntu 22.04.
        # This is not an issues as not setting the SHOW flag does not seem to have
        # any negative effects.

        desc.WindowAttributes = int(
            WindowAttributeEnum.SHOW
            | WindowAttributeEnum.MOVEABLE
            | WindowAttributeEnum.SIZEABLE
            | WindowAttributeEnum.CLOSEABLE
            | WindowAttributeEnum.BORDER
        )

        dialog_peer = self.tk.createWindow(desc)

        self._init_handlers()
        glbs = GblEvents()

        self._dialog = cast("WindowType", dialog_peer)

        self._dialog.setVisible(False)
        self._dialog.setTitle(self._title)
        self._init_code()
        self._init_buttons()
        self._init_menu_label()
        self._dialog.addWindowListener(WindowListener(self))

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
        self._fn_on_menu_lbl_mouse_entered = self._on_menu_lbl_mouse_entered
        self._fn_on_menu_range_select_result = self._on_menu_range_select_result

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

    def windowClosed(self, event: EventObject) -> None:
        """is invoked when a window has been closed."""
        self._log.debug("Window Closed")

    def disposing(self, event: EventObject) -> None:
        self._log.debug("Disposing")

    # endregion XTopWindowListener

    # self._fn_on_menu_lbl_mouse_entered = self.on_menu_lbl_mouse_entered

    def _init_menu_label(self) -> None:
        """Add a fixed text label to the dialog control"""
        self._mnu_lbl_item = CtlFixedText.create(
            self._dialog,
            Label="☰",
            x=0,
            y=0,
            width=14,
            height=14,
        )
        # lbl_item.font_descriptor = self._mnu_lbl_fd
        self._mnu_lbl_item.add_event_mouse_entered(self._fn_on_menu_lbl_mouse_entered)
        # self._mnu_lbl_item.add_event_mouse_pressed(self._fn_on_menu_lbl_mouse_click)

    def _init_buttons(self) -> None:
        """Add OK, Cancel and Info buttons to dialog control"""
        sz = self._dialog.getPosSize()

        btn_y = sz.Height - DialogPython.BUTTON_HEIGHT - self._padding
        btn_x = sz.Width - DialogPython.BUTTON_WIDTH - self._padding

        self._ctl_btn_cancel = CtlButton.create(
            self._dialog,
            x=btn_x,
            y=btn_y,
            width=DialogPython.BUTTON_WIDTH,
            height=DialogPython.BUTTON_HEIGHT,
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
        txt_y = DialogPython.HEADER + self._margin

        txt_height = DialogPython.HEIGHT - DialogPython.FOOTER - (self._margin * 2) - txt_y
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
        # self._set_tab_index(self._event_text)

    # endregion Init

    # region resize
    def resize_buttons(self, sz: Rectangle) -> None:

        btn_y = sz.Height - DialogPython.BUTTON_HEIGHT - self._padding
        btn_x = sz.Width - DialogPython.BUTTON_WIDTH - self._padding
        self._ctl_btn_cancel.view.setPosSize(
            btn_x, btn_y, DialogPython.BUTTON_WIDTH, DialogPython.BUTTON_HEIGHT, PosSize.POSSIZE
        )

        x = btn_x - DialogPython.BUTTON_WIDTH - self._margin
        self._ctl_btn_ok.view.setPosSize(
            x, btn_y, DialogPython.BUTTON_WIDTH, DialogPython.BUTTON_HEIGHT, PosSize.POSSIZE
        )

    def resize_code(self, sz: Rectangle) -> None:
        txt_sz = self._code.view.getPosSize()
        width = sz.Width - (self._margin * 2)
        txt_height = sz.Height - DialogPython.FOOTER - (self._margin * 2) - txt_sz.Y
        self._code.view.setPosSize(txt_sz.X, txt_sz.Y, width, txt_height, PosSize.POSSIZE)

    def resize(self) -> None:
        sz = self._dialog.getPosSize()
        if sz.Height < DialogPython.MIN_HEIGHT:
            return
        if sz.Width < DialogPython.MIN_WIDTH:
            return
        self.resize_buttons(sz)
        self.resize_code(sz)

    # endregion resize
    # region Code Edit

    def clear(self):
        """Clear edit area"""
        self._code.text = ""

    # region Read/Write

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

    # region Key Handlers
    def onkey_1282(self, modifiers: str) -> bool:  # TAB
        """Catch TAB keyboard entry"""
        if not modifiers:
            # self._log.debug("TAB")
            sel = self._code.view.getSelection()
            self._write(" " * DialogPython.NB_TAB, (sel.Min, sel.Max))
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

    # region Handle Results
    def _handle_results(self, result: int) -> None:
        """Display a message if the OK button has been clicked"""
        if result == MessageBoxResultsEnum.OK.value:
            _ = self._doc.msgbox(
                msg="All done",
                title="Finished",
                boxtype=MessageBoxType.INFOBOX,
            )

    # endregion Handle Results

    # region Event Handlers

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

    # region button handlers

    # endregion button handlers
    def on_btn_ok_click(self, source: Any, event: EventArgs, control_src: CtlButton) -> None:
        self.end_dialog(1)

    def on_btn_cancel_click(self, source: Any, event: EventArgs, control_src: CtlButton) -> None:
        self.end_dialog(0)

    # endregion Event Handlers

    def get_parent(self):
        """Returns parent frame"""
        return Lo.desktop.get_active_frame().getContainerWindow()

    def _update_config(self) -> None:
        sz = self._dialog.getPosSize()
        self._cfg.width = sz.Width
        self._cfg.height = sz.Height
        self._cfg.x = sz.X
        self._cfg.y = sz.Y
        self._cfg.save()

    # region Show Dialog
    def end_dialog(self, result: int = 0) -> None:
        """Terminate dialog"""
        self._log.debug("End Dialog Called.")
        try:
            self._update_config()
        except Exception as e:
            self._log.error(f"Error saving configuration: {e}", exc_info=True)
        self._dialog.endDialog(result)

    def show(self) -> int:

        self._is_shown = True
        self._dialog.addTopWindowListener(self)

        # while self._is_shown:
        #     self._dialog.setVisible(self._is_shown)
        #     time.sleep(0.3)

        result = self._dialog.execute()
        # self._handle_results(result)
        self._dialog.dispose()
        return result
        return 1

    # endregion Show Dialog

    def _set_tab_index(self, ctl: DialogControlBase) -> None:
        ctl.tab_index = self._current_tab_index
        self._current_tab_index += 1

    # region Menu
    def _get_main_menu(self) -> PopupMenu:
        if self._main_menu is None:
            self._main_menu = self._mnu.get_popup_menu()
            self._main_menu.subscribe_all_item_selected(self._fn_on_menu_select)
        return self._main_menu

    def _display_popup(self, control_src: CtlFixedText) -> None:
        try:
            pm = self._get_main_menu()
            view = control_src.view
            pm.execute(self._dialog, view.getPosSize(), 0)  # type: ignore
        except Exception as e:
            self._log.error(f"Error displaying popup: {e}", exc_info=True)

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

    def _on_menu_lbl_mouse_entered(
        self,
        src: Any,
        event: EventArgs,
        control_src: CtlFixedText,
        *args,
        **kwargs,
    ) -> None:
        self._display_popup(control_src)

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

    # endregion Menu

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
    def doc(self) -> OfficeDocumentT:
        """Gets the current document."""
        return self._doc

    # endregion properties
