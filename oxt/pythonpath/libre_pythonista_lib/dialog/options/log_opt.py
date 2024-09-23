# region Imports
from __future__ import annotations
import uno
from typing import Any, cast, TYPE_CHECKING
import logging

from ooo.dyn.awt.push_button_type import PushButtonType
from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.awt.font_descriptor import FontDescriptor

from ooodev.dialog.msgbox import MessageBoxResultsEnum, MessageBoxType, MessageBoxButtonsEnum
from ooodev.dialog import BorderKind
from ooodev.events.args.event_args import EventArgs
from ooodev.loader import Lo
from ooodev.utils.kind.tri_state_kind import TriStateKind
from ooodev.utils.info import Info
from ooodev.utils.color import StandardColor

from ...doc_props.calc_props import CalcProps
from ...event.shared_event import SharedEvent
from ...const.event_const import LOG_OPTIONS_CHANGED

if TYPE_CHECKING:
    from com.sun.star.awt import ActionEvent
    from com.sun.star.awt import ItemEvent
    from ooodev.dialog.dl_control import CtlRadioButton, CtlCheckBox

    from .....___lo_pip___.config import Config
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver

# endregion Imports


class LogOpt:
    # pylint: disable=unused-argument
    # region Init
    def __init__(self) -> None:
        self._doc = Lo.current_doc
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init Class")
        self._cfg = Config()  # singleton
        self._rr = ResourceResolver(ctx=self._doc.lo_inst.get_context())
        self._calc_props = CalcProps(self._doc)
        self._border_kind = BorderKind.BORDER_SIMPLE
        self._width = 400
        self._height = 320
        self._btn_width = 100
        self._btn_height = 30
        self._margin = 6
        self._box_height = 16
        self._title = self._rr.resolve_string("title11")  # Logging Options
        self._msg = self._rr.resolve_string("strDocLogOptMsg")
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 8
        else:
            self._padding = 12
        self._current_tab_index = 1
        self._group1_opt: CtlRadioButton | None = None
        self._include_extra_info = self._get_extra_tri_state()

        # get or set a font descriptor. This helps to keep the font consistent across different platforms.
        fd = Info.get_font_descriptor("Liberation Serif", "Regular")
        if fd is None:
            fd = FontDescriptor(
                CharacterWidth=100.0,
                Kerning=True,
                WordLineMode=False,
                Pitch=2,
                Weight=100,
            )
        fd.Height = 10
        self._fd = fd
        self._init_dialog()
        self._log.debug("Init Class Done.")

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        self._init_handlers()
        self._dialog = self._doc.create_dialog(x=-1, y=-1, width=self._width, height=self._height, title=self._title)
        self._dialog.set_visible(False)
        self._dialog.create_peer()
        self._init_label()
        self._init_log_format()
        self._init_group_boxes()
        self._init_radio_controls()
        self._init_buttons()
        self._init_check_boxes()

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

        self._fn_on_group1_changed = self.on_group1_changed
        self._fn_button_action_preformed = self.on_button_action_preformed
        self._fn_on_check_changed = self.on_check_changed

    def _get_extra_tri_state(self) -> TriStateKind:
        ts = self._calc_props.include_extra_err_info
        if ts:
            return TriStateKind.CHECKED
        return TriStateKind.NOT_CHECKED

    def _init_label(self) -> None:
        """Add a fixed text label to the dialog control"""
        self._ctl_main_lbl = self._dialog.insert_label(
            label=self._msg,
            x=self._margin,
            y=self._padding,
            width=self._width - (self._padding * 2),
            height=self._box_height,
        )
        self._ctl_main_lbl.set_font_descriptor(self._fd)
        self._ctl_main_lbl.font_descriptor.weight = 150  # make bold

    def _init_log_format(self) -> None:
        sz = self._ctl_main_lbl.view.getPosSize()

        self._ctl_format_lbl = self._dialog.insert_label(
            label=self._rr.resolve_string("strLogFormat"),
            x=sz.X,
            y=self._padding + sz.Y + sz.Height,
            width=sz.Width,
            height=self._box_height,
        )
        self._ctl_format_lbl.set_font_descriptor(self._fd)

        lbl_sz = self._ctl_format_lbl.view.getPosSize()

        self._ctl_format_text = self._dialog.insert_text_field(
            text=self._calc_props.log_format,
            x=lbl_sz.X,
            y=self._padding + lbl_sz.Y + lbl_sz.Height,
            width=lbl_sz.Width,
            height=lbl_sz.Height + 5,
            border=self._border_kind,
            ReadOnly=False,
            MultiLine=False,
            AutoVScroll=True,
        )

    def _init_group_boxes(self) -> None:
        # self._ctl_format_text
        sz = self._ctl_format_text.view.getPosSize()
        self._ctl_gb1 = self._dialog.insert_group_box(
            x=self._margin,
            y=self._padding + sz.Y + sz.Height,
            height=140,  # self._height - (sz_lbl.X + sz_lbl.Height) - self._btn_height - (self._padding * 3),
            width=self._width - (self._margin * 2),
            label=self._rr.resolve_string("log01"),
        )
        self._ctl_gb1.set_font_descriptor(self._fd)
        self._ctl_gb1.font_descriptor.weight = 150  # make bold

    def _init_buttons(self) -> None:
        """Add OK, Cancel and Info buttons to dialog control"""
        self._ctl_btn_cancel = self._dialog.insert_button(
            label=self._rr.resolve_string("dlg02"),
            x=self._width - self._btn_width - self._margin,
            y=self._height - self._btn_height - self._padding,
            width=self._btn_width,
            height=self._btn_height,
            btn_type=PushButtonType.CANCEL,
        )
        self._ctl_btn_cancel.set_font_descriptor(self._fd)
        self._ctl_btn_cancel.text_color = StandardColor.BLACK
        self._ctl_btn_cancel.background_color = StandardColor.RED_LIGHT1
        self._ctl_btn_cancel.help_text = self._rr.resolve_string("dlg02")

        sz = self._ctl_btn_cancel.view.getPosSize()
        self._ctl_btn_ok = self._dialog.insert_button(
            label=self._rr.resolve_string("dlg01"),
            x=sz.X - sz.Width - self._margin,
            y=sz.Y,
            width=self._btn_width,
            height=self._btn_height,
            btn_type=PushButtonType.OK,
            DefaultButton=True,
        )
        self._ctl_btn_ok.set_font_descriptor(self._fd)
        self._ctl_btn_ok.text_color = StandardColor.BLACK
        self._ctl_btn_ok.background_color = StandardColor.GREEN_LIGHT1
        self._ctl_btn_ok.help_text = self._rr.resolve_string("dlg01")

        self._ctl_btn_reset = self._dialog.insert_button(
            label=self._rr.resolve_string("dlgResetLogOpt"),
            x=self._margin,
            y=sz.Y,
            width=self._btn_width,
            height=self._btn_height,
        )
        self._ctl_btn_reset.set_font_descriptor(self._fd)
        self._ctl_btn_reset.view.setActionCommand("RESET")
        self._ctl_btn_reset.model.HelpText = self._rr.resolve_string("dlgHlpResetLogOpt")
        self._ctl_btn_reset.add_event_action_performed(self._fn_button_action_preformed)

    def _get_log_level(self) -> int:
        log_level = self._calc_props.log_level
        if log_level <= 0:
            return 0
        if log_level >= logging.CRITICAL:
            return 5
        if log_level >= logging.ERROR:
            return 4
        if log_level >= logging.WARNING:
            return 3
        if log_level >= logging.INFO:
            return 2
        # default logging.DEBUG
        return 1

    def _init_radio_controls(self) -> None:
        # None
        # Debug
        # Normal
        # Warning
        # Error
        # Critical
        labels = []
        labels.append(self._rr.resolve_string("log02"))
        labels.append(self._rr.resolve_string("log03"))
        labels.append(self._rr.resolve_string("log04"))
        labels.append(self._rr.resolve_string("log08"))
        labels.append(self._rr.resolve_string("log09"))
        labels.append(self._rr.resolve_string("log10"))

        db_vals = [0, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        def get_index() -> int:
            log_level = self._calc_props.log_level
            if log_level <= 0:
                return 0
            if log_level >= logging.CRITICAL:
                return 5
            if log_level >= logging.ERROR:
                return 4
            if log_level >= logging.WARNING:
                return 3
            if log_level >= logging.INFO:
                return 2
            # default logging.DEBUG
            return 1

        selected_index = get_index()

        def get_state(index: int, selected_index: int) -> int:
            if index == selected_index:
                return 1
            return 0

        sz_gb1 = self._ctl_gb1.view.getPosSize()
        self._rb1 = self._dialog.insert_radio_button(
            label=labels[0],
            x=sz_gb1.X + self._margin,
            y=sz_gb1.Y + self._box_height,
            width=sz_gb1.Width - (self._margin * 2),
            height=20,
        )

        self._rb1.set_font_descriptor(self._fd)
        self._ctl_gb1.model.TabIndex = self._current_tab_index
        self._current_tab_index += 1

        self._rb1.model.State = get_state(0, selected_index)
        self._rb1.tab_index = self._current_tab_index
        self._rb1.tag = f"{db_vals[0]}"
        self._current_tab_index += 1

        extra = 5
        self._rb1.add_event_item_state_changed(self._fn_on_group1_changed)
        rb1_sz = self._rb1.view.getPosSize()

        for i in range(1, extra + 1):
            radio_btn = self._dialog.insert_radio_button(
                label=labels[i],
                x=rb1_sz.X,
                y=rb1_sz.Y + (rb1_sz.Height * i),
                width=rb1_sz.Width,
                height=rb1_sz.Height,
            )
            radio_btn.set_font_descriptor(self._rb1.font_descriptor.component)
            radio_btn.tab_index = self._current_tab_index
            radio_btn.model.State = get_state(i, selected_index)
            radio_btn.tag = f"{db_vals[i]}"
            self._current_tab_index += 1
            radio_btn.add_event_item_state_changed(self._fn_on_group1_changed)

        self._current_tab_index += 1

    def _init_check_boxes(self) -> None:
        # self._ctl_format_text
        sz_gb1 = self._ctl_gb1.view.getPosSize()
        self._ctl_chk_extra_info = self._dialog.insert_check_box(
            x=self._margin,
            y=self._padding + sz_gb1.Y + sz_gb1.Height,
            height=14,  # self._height - (sz_lbl.X + sz_lbl.Height) - self._btn_height - (self._padding * 3),
            width=self._width - (self._margin * 2),
            label=self._rr.resolve_string("strIncExErrInfo"),
            tri_state=False,
            state=self._include_extra_info,
            border=self._border_kind,
        )
        self._ctl_chk_extra_info.set_font_descriptor(self._fd)
        self._ctl_chk_extra_info.help_text = self._rr.resolve_string("strIncExErrInfo")
        self._ctl_chk_extra_info.add_event_item_state_changed(self._fn_on_check_changed)

    # endregion Init

    # region Handle Results
    def _handle_results(self, result: int) -> None:
        """Display a message if the OK button has been clicked"""
        with self._log.indent(True):
            try:
                if result == MessageBoxResultsEnum.OK.value:
                    if self._group1_opt:
                        if self._log.is_debug:
                            self._log.debug(f"Group 1 Tag: {self._group1_opt.tag}")
                        self._calc_props.log_level = int(self._group1_opt.tag)
                    else:
                        self._log.debug("Group 1 Option is None")
                        self._calc_props.log_level = logging.INFO
                    fmt = self._ctl_format_text.text
                    self._log.debug(f"Log Format: {fmt}")
                    self._calc_props.log_format = fmt
                    self._calc_props.include_extra_err_info = self._include_extra_info == TriStateKind.CHECKED
                    SharedEvent().trigger_event(LOG_OPTIONS_CHANGED, EventArgs(self))
            except Exception:
                self._log.exception("Error in _handle_results")

    def _reset_options(self) -> None:
        result = self._doc.msgbox(
            msg=self._rr.resolve_string("mbmsg005"),
            title=self._rr.resolve_string("mbtitle005"),
            buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
            boxtype=MessageBoxType.QUERYBOX,
        )
        if result == MessageBoxResultsEnum.YES:
            self._calc_props.log_level = logging.INFO
            self._calc_props.include_extra_err_info = False
            self._calc_props.log_format = self._cfg.lp_default_log_format
            self._dialog.end_dialog(MessageBoxResultsEnum.CANCEL.value)
            SharedEvent().trigger_event(LOG_OPTIONS_CHANGED, EventArgs(self))

    # endregion Handle Results

    # region Event Handlers
    def on_group1_changed(self, src: Any, event: EventArgs, control_src: CtlRadioButton, *args, **kwargs) -> None:
        itm_event = cast("ItemEvent", event.event_data)
        with self._log.indent(True):
            if self._log.is_debug:
                self._log.debug(f"Group 1 Item ID: {itm_event.ItemId}")
                self._log.debug(f"Group 1 Tab Index: {control_src.tab_index}")
                self._log.debug(f"Group 1 Tab Name: {control_src.model.Name}")
        self._group1_opt = control_src

    def on_check_changed(self, src: Any, event: EventArgs, control_src: CtlCheckBox, *args, **kwargs) -> None:
        self._log.debug(f"Check Changed: {control_src.state}")
        self._include_extra_info = control_src.state

    def on_button_action_preformed(self, src: Any, event: EventArgs, control_src: Any, *args, **kwargs) -> None:
        """Method that is fired when Info button is clicked."""
        itm_event = cast("ActionEvent", event.event_data)
        with self._log.indent(True):
            self._log.debug(f"Button Action Command: {itm_event.ActionCommand}")
        if itm_event.ActionCommand == "RESET":
            self._reset_options()

    # endregion Event Handlers

    # region Show Dialog
    def show(self) -> int:
        # make sure the document is active.
        self._doc.activate()
        window = self._doc.get_frame().getContainerWindow()
        ps = window.getPosSize()
        x = round(ps.Width / 2 - self._width / 2)
        y = round(ps.Height / 2 - self._height / 2)
        self._dialog.set_pos_size(x, y, self._width, self._height, PosSize.POSSIZE)
        self._dialog.set_visible(True)
        result = self._dialog.execute()
        self._handle_results(result)
        self._dialog.dispose()
        return result

    # endregion Show Dialog
