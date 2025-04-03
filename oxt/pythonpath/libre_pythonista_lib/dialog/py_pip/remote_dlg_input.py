from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooo.dyn.awt.push_button_type import PushButtonType
from ooo.dyn.awt.pos_size import PosSize
from ooo.dyn.awt.font_descriptor import FontDescriptor

from ooodev.dialog import BorderKind
from ooodev.events.args.event_args import EventArgs
from ooodev.loader import Lo
from ooodev.utils.kind.tri_state_kind import TriStateKind
from ooodev.utils.info import Info
from ooodev.utils.color import StandardColor
from ooodev.utils.sys_info import SysInfo


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ooodev.dialog.dl_control import CtlCheckBox
    from oxt.___lo_pip___.config import Config
    from oxt.___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
else:
    from ___lo_pip___.config import Config
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc_props.calc_props2 import CalcProps2

    OfficeDocumentT = Any


class RemoteDlgInput(LogMixin):
    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._doc = cast(OfficeDocumentT, Lo.current_doc)
        self.log.debug("Init Class")
        self._cfg = Config()  # singleton
        self._rr = ResourceResolver(ctx=self._doc.lo_inst.get_context())
        self._calc_props = CalcProps2()
        self._platform = SysInfo.get_platform()
        self._border_kind = BorderKind.BORDER_SIMPLE
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 10
        else:
            self._padding = 14

        if self._platform == SysInfo.PlatformEnum.MAC:
            self._height = 150
            self._box_height = 30
            self._padding += 4
        else:
            self._height = 120
            self._box_height = 20

        self._width = 400
        self._btn_width = 100
        self._btn_height = 30
        self._margin = 6
        self._title = self._rr.resolve_string("title13")  # Install Pip Package

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

        self._tri_force_install = TriStateKind.NOT_CHECKED

        self._init_dialog()

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        self._init_handlers()
        self._dialog = self._doc.create_dialog(x=-1, y=-1, width=self._width, height=self._height, title=self._title)
        self._dialog.set_visible(False)
        self._dialog.create_peer()
        self._init_buttons()
        self._init_input()
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

        self._fn_button_action_preformed = self.on_button_action_preformed
        self._fn_on_check_changed = self.on_check_changed

    def _init_input(self) -> None:
        """Add input fields"""
        self._ctl_input = self._dialog.insert_text_field(
            x=self._margin,
            y=self._padding,
            width=self._width - 2 * self._margin,
            height=self._box_height,
            border=self._border_kind,
        )
        self._ctl_input.set_font_descriptor(self._fd)
        self._ctl_input.help_text = self._rr.resolve_string("msg11")

    def _init_buttons(self) -> None:
        """Add OK, Cancel"""
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

    def _init_check_boxes(self) -> None:
        # self._ctl_format_text
        sz_txt = self._ctl_input.view.getPosSize()
        self._ctl_chk_force_install = self._dialog.insert_check_box(
            x=sz_txt.X,
            y=self._padding + sz_txt.Y + sz_txt.Height,
            height=14,
            width=self._width - (self._margin * 2),
            label=self._rr.resolve_string("strForceInstall"),
            tri_state=False,
            state=self._tri_force_install,
            border=self._border_kind,
        )
        self._ctl_chk_force_install.set_font_descriptor(self._fd)
        self._ctl_chk_force_install.help_text = self._rr.resolve_string("strForceInstallHelp")
        self._ctl_chk_force_install.add_event_item_state_changed(self._fn_on_check_changed)

    def on_button_action_preformed(self, src: Any, event: EventArgs, control_src: Any, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ANN401
        """Method that is fired when Info button is clicked."""
        pass

    def on_check_changed(self, src: Any, event: EventArgs, control_src: CtlCheckBox, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ANN401
        self.log.debug(f"Check Changed: {control_src.state}")
        self._tri_force_install = control_src.state

    def _clean_pkg_name(self, pkg_name: str) -> str:
        """Remove any leading and trailing spaces and quotes."""
        s = pkg_name.strip()
        s = s.replace(" ", "")
        s = s.replace("'", "")
        s = s.replace('"', "")
        return s

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
        self._dialog.dispose()
        return result

    # endregion Show Dialog

    # region Properties
    @property
    def force_install(self) -> bool:
        """
        Gets if the user has selected to force install the package.
        """
        return self._tri_force_install == TriStateKind.CHECKED

    @property
    def package_name(self) -> str:
        """
        Gets the package name entered by the user.
        """
        return self._clean_pkg_name(self._ctl_input.text)

    # endregion Properties
