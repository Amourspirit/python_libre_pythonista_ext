"""
This class is a copy of OooDev's Input.
It is here because the OooDev Input needs formatting updates.
On MacOs the Input text box is too small and the font is too small.
"""

from typing import TYPE_CHECKING, cast
import uno  # pylint: disable=unused-import

from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.awt.push_button_type import PushButtonType
from ooo.dyn.awt.font_descriptor import FontDescriptor

from ooodev.utils.kind.border_kind import BorderKind
from ooodev.dialog.dialogs import Dialogs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.event_singleton import _Events
from ooodev.events.gbl_named_event import GblNamedEvent
from ooodev.exceptions import ex as mEx
from ooodev.loader import lo as mLo
from ooodev.utils import info as mInfo
from ooodev.utils.sys_info import SysInfo

if TYPE_CHECKING:
    from com.sun.star.frame import XFrame


class Input:
    @staticmethod
    def get_input(
        title: str,
        msg: str,
        input_value: str = "",
        ok_lbl: str = "OK",
        cancel_lbl: str = "Cancel",
        is_password: bool = False,
    ) -> str:
        """
        Displays an input box and returns the results.

        |lo_unsafe|

        Args:
            title (str): Title for the dialog
            msg (str): Message to display such as "Input your Name"
            input_value (str, optional): Value of input box when first displayed.
            ok_lbl (str, optional): OK button Label. Defaults to "OK".
            cancel_lbl (str, optional): Cancel Button Label. Defaults to "Cancel".
            is_password (bool, optional): Determines if the input box is masked for password input. Defaults to ``False``.

        Raises:
            CancelEventError: If the dialog creation was cancelled.

        Returns:
            str: The value of input or empty string.

        Note:
            Raises a global event ``GblNamedEvent.INPUT_BOX_CREATING`` before creating the dialog.
            The event args are of type ``CancelEventArgs``.
            The ``event_data`` is a dictionary that contains the following key:

            - ``msg``: The message to display.
            - ``title``: The title of the dialog.
            - ``input_value``: The value of the input box when first displayed.
            - ``ok_lbl``: The label for the OK button.
            - ``cancel_lbl``: The label for the Cancel button.
            - ``is_password``: Determines if the input box is masked for password input.
            - ``frame``: The frame of the dialog. If not set, the frame of the current document is used.

            The default ``frame`` is ``None``. If set value must be a ``XFrame`` object.

            If the event is cancelled, the ``result`` value of ``event_data` if set will be returned.
            Otherwise if the event is not handled, a ``CancelEventError`` is raised.
        """
        cargs = CancelEventArgs(Input.get_input.__qualname__)
        cargs.event_data = {
            "msg": msg,
            "title": title,
            "input_value": input_value,
            "ok_lbl": ok_lbl,
            "cancel_lbl": cancel_lbl,
            "is_password": is_password,
            "frame": None,
        }
        _Events().trigger(GblNamedEvent.INPUT_BOX_CREATING, cargs)

        if cargs.cancel is True:
            if "result" in cargs.event_data:
                return cast(str, cargs.event_data["result"])
            if cargs.handled is False:
                raise mEx.CancelEventError(cargs, "Dialog creation was cancelled.")

        msg = cast(str, cargs.event_data["msg"])
        title = cast(str, cargs.event_data["title"])
        input_value = cast(str, cargs.event_data["input_value"])
        ok_lbl = cast(str, cargs.event_data["ok_lbl"])
        cancel_lbl = cast(str, cargs.event_data["cancel_lbl"])
        is_password = cast(bool, cargs.event_data["is_password"])
        platform = SysInfo().get_platform()

        # get or set a font descriptor. This helps to keep the font consistent across different platforms.
        fd = mInfo.Info.get_font_descriptor("Liberation Serif", "Regular")
        if fd is None:
            fd = FontDescriptor(
                CharacterWidth=100.0,
                Kerning=True,
                WordLineMode=False,
                Pitch=2,
                Weight=100,
            )
        if platform == SysInfo.PlatformEnum.MAC:
            fd.Height = 14
            height = 140
            box_height = 30
        else:
            fd.Height = 10
            height = 120
            box_height = 20

        btn_height = 30
        vert_margin = 12
        btn_fd_height = 12
        width = 450
        btn_width = 100
        margin = 6
        border_kind = BorderKind.BORDER_SIMPLE
        dialog = Dialogs.create_dialog(
            x=-1,
            y=-1,
            width=width,
            height=height,
            title=title,
        )

        ctl_lbl = Dialogs.insert_label(
            dialog_ctrl=dialog.control, label=msg, x=margin, y=margin, width=width - (margin * 2), height=box_height
        )
        ctl_lbl.font_descriptor = fd
        sz = ctl_lbl.view.getPosSize()
        if is_password:
            txt_input = Dialogs.insert_password_field(
                dialog_ctrl=dialog.control,
                text=input_value,
                x=sz.X,
                y=sz.Height + sz.Y + vert_margin,
                width=sz.Width,
                height=box_height,
                border=border_kind,
            )
        else:
            txt_input = Dialogs.insert_text_field(
                dialog_ctrl=dialog.control,
                text=input_value,
                x=sz.X,
                y=sz.Height + sz.Y + vert_margin,
                width=sz.Width,
                height=box_height,
                border=border_kind,
            )
        txt_input.font_descriptor = fd
        ctl_btn_cancel = Dialogs.insert_button(
            dialog_ctrl=dialog.control,
            label=cancel_lbl,
            x=width - btn_width - margin,
            y=height - btn_height - vert_margin,
            width=btn_width,
            height=btn_height,
            btn_type=PushButtonType.CANCEL,
        )
        ctl_btn_cancel.font_descriptor = fd
        ctl_btn_cancel.font_descriptor.height = btn_fd_height
        sz = ctl_btn_cancel.view.getPosSize()
        ctl_btn_ok = Dialogs.insert_button(
            dialog_ctrl=dialog.control,
            label=ok_lbl,
            x=sz.X - sz.Width - margin,
            y=sz.Y,
            width=btn_width,
            height=btn_height,
            btn_type=PushButtonType.OK,
            DefaultButton=True,
        )
        ctl_btn_ok.set_font_descriptor(ctl_btn_cancel.font_descriptor)

        frame = cast("XFrame", cargs.event_data["frame"])
        if frame is not None:
            window = frame.getContainerWindow()
        else:
            window = mLo.Lo.get_frame().getContainerWindow()
        ps = window.getPosSize()
        x = round(ps.Width / 2 - width / 2)
        y = round(ps.Height / 2 - height / 2)
        dialog.set_pos_size(x, y, width, height, PosSize.POSSIZE)
        dialog.set_visible(True)
        ret = txt_input.text if dialog.execute() else ""  # type: ignore
        dialog.dispose()
        return ret
