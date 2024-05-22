# region Imports
from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple
import uno
from com.sun.star.awt import Selection
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import TOP
from ooo.dyn.awt.window_attribute import WindowAttributeEnum
from ooo.dyn.awt.rectangle import Rectangle
from ooo.dyn.awt.font_descriptor import FontDescriptor
from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.style.vertical_alignment import VerticalAlignment
from ooodev.dialog import BorderKind
from ooodev.dialog.msgbox import MessageBoxResultsEnum, MessageBoxType
from ooodev.loader import Lo
from ooodev.dialog.dl_control import CtlButton, CtlTextEdit, CtlFixedText
from ooodev.events.args.event_args import EventArgs
from .window_listener import WindowListener
from .key_handler import KeyHandler
from ...res.res_resolver import ResResolver
from .dialog_menu import DialogMenu


# from .focus_listener import FocusListener

# from ooodev.dialog.dialog import Dialog
from ooodev.dialog.dialogs import Dialogs

if TYPE_CHECKING:
    from com.sun.star.awt import MenuEvent
    from ooodev.dialog.dl_control.ctl_base import DialogControlBase
    from ooodev.gui.menu.popup_menu import PopupMenu
    from ..window_type import WindowType

# endregion Imports


class DialogPython:
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
        self._rr = ResResolver(ctx)  # singleton
        self._doc = Lo.current_doc
        self._border_kind = BorderKind.BORDER_3D
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

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        rect = Rectangle()
        rect.Width = self._width
        rect.Height = self._height
        ps = self.parent.getPosSize()
        rect.X = int((ps.Width - self._width) / 2 - 50)
        rect.Y = int((ps.Height - self._height) / 2 - 100)

        desc = WindowDescriptor()
        desc.Type = TOP
        desc.WindowServiceName = "dialog"
        desc.ParentIndex = -1
        desc.Bounds = rect
        desc.WindowAttributes = int(
            WindowAttributeEnum.SHOW
            | WindowAttributeEnum.MOVEABLE
            | WindowAttributeEnum.SIZEABLE
            | WindowAttributeEnum.CLOSEABLE
            | WindowAttributeEnum.BORDER
        )

        dialog_peer = self.tk.createWindow(desc)

        self._init_handlers()
        self._dialog = cast("WindowType", dialog_peer)
        # self._dialog = self._doc.create_dialog(x=-1, y=-1, width=self._width, height=self._height, title=self._title)
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
        print("Write", f'Data:"{data}"', "Selection", sel)
        self._code.view.insertText(Selection(*sel), data)

    # endregion Read/Write
    # endregion Code Edit

    # region Key Handlers
    def onkey_1282(self, modifiers: str) -> bool:  # TAB
        """Catch TAB keyboard entry"""
        if not modifiers:
            # print("TAB")
            sel = self._code.view.getSelection()
            self._write(" " * DialogPython.NB_TAB, (sel.Min, sel.Max))
            return True
        return False

    # endregion Key Handlers

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
        print("Text Changed", self.end)
        sel = control_src.view.getSelection()
        print("Selection:", sel.Min, sel.Max)

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
        print("Focus Gained")

    def on_code_focus_lost(self, source: Any, event: EventArgs, control_src: CtlTextEdit) -> None:
        self.code_focused = False
        self.tk.removeKeyHandler(self.keyhandler)
        print("Focus Lost")

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

    # region Show Dialog
    def end_dialog(self, result: int = 0) -> None:
        """Terminate dialog"""
        self._dialog.endDialog(result)

    def show(self) -> int:

        self._dialog.setVisible(True)
        result = self._dialog.execute()
        # self._handle_results(result)
        self._dialog.dispose()
        return result

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
        sz = control_src.view.getPosSize()
        rect = Rectangle(
            X=sz.X,
            Y=sz.Y,
            Width=10,
            Height=10,
        )
        pm = self._get_main_menu()
        pm.execute(self._dialog, rect, 0)

    def _on_menu_select(self, src: Any, event: EventArgs, menu: PopupMenu) -> None:
        print("Menu Selected")
        me = cast("MenuEvent", event.event_data)
        command = menu.get_command(me.MenuId)
        # self._write_line(f"Menu Selected: {command}, Menu ID: {me.MenuId}")

        if command == ".uno:py_validate":
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
        return
        if command == ".uno:exitok":
            self._dialog.end_dialog(MessageBoxResultsEnum.OK.value)
            return
        if command in self._execute_cmds and menu.is_dispatch_cmd(command):
            menu.execute_cmd(command)

    def _on_menu_lbl_mouse_entered(
        self,
        src: Any,
        event: EventArgs,
        control_src: CtlFixedText,
        *args,
        **kwargs,
    ) -> None:
        self._display_popup(control_src)

    # endregion Menu

    # region properties

    @property
    def res_resolver(self) -> ResResolver:
        return self._rr

    @property
    def text(self) -> str:
        return self._code.text

    # endregion properties
