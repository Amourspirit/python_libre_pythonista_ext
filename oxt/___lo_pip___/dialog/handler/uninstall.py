from __future__ import annotations
from typing import Any, TYPE_CHECKING, Tuple, cast, Set

# from pprint import pformat

import uno
import unohelper

from com.sun.star.awt import XActionListener  # type: ignore
from com.sun.star.awt import XContainerWindowEventHandler  # type: ignore
from com.sun.star.beans import PropertyChangeEvent  # type: ignore # struct
from com.sun.star.beans import XPropertyChangeListener  # type: ignore
from com.sun.star.awt.MessageBoxType import QUERYBOX, INFOBOX, ERRORBOX  # type: ignore
from com.sun.star.awt.PushButtonType import STANDARD
from com.sun.star.awt import PosSize

from ..dialog_base import DialogBase
from ...basic_config import BasicConfig
from ...lo_util.resource_resolver import ResourceResolver
from ...settings.settings import Settings
from ...oxt_logger import OxtLogger
from ..message_dialog import MessageDialog


if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlDialog  # type: ignore # service
    from com.sun.star.awt import UnoControlCheckBoxModel  # type: ignore
    from com.sun.star.awt import UnoControlCheckBox  # type: ignore
    from com.sun.star.awt import UnoControlButton  # type: ignore # service
    from com.sun.star.beans import XPropertySet
    from ...install.install_pkg import InstallPkg
else:
    UnoControlButton = Any


class ButtonUninstallListener(XActionListener, unohelper.Base):
    def __init__(self, dialog_handler: "OptionsDialogUninstallHandler") -> None:
        XActionListener.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("ButtonListener.__init__")
        self.dialog_handler = dialog_handler
        self._log.debug("ButtonListener.__init__ done")
        self._config = BasicConfig()

    def disposing(self, Source: Any) -> None:  # noqa: ANN401, N803
        pass

    def actionPerformed(self, rEvent: Any) -> None:  # noqa: ANN401, N802, N803
        # sourcery skip: extract-method
        self._log.debug("ButtonListener.actionPerformed")
        try:
            cmd = str(rEvent.ActionCommand)
            self._log.debug(f"ButtonListener.actionPerformed cmd: {cmd}")
            if cmd == "UninstallItems":
                if not self.dialog_handler.uninstall_pkgs:
                    self._log.debug("ButtonListener.actionPerformed: uninstall_pkg is False")
                    title = self.dialog_handler._resource_resolver.resolve_string("mbtitle017")
                    msg = self.dialog_handler._resource_resolver.resolve_string("mbmsg017")
                    _ = MessageDialog(
                        self.dialog_handler.ctx,
                        title=title,
                        message=msg,
                        type=INFOBOX,
                    ).execute()
                    return
                title = self.dialog_handler._resource_resolver.resolve_string("mbtitle018")
                msg = self.dialog_handler._resource_resolver.resolve_string("mbmsg018")
                # buttons: https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
                # results: https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxResults.html

                result = MessageDialog(
                    self.dialog_handler.ctx,
                    title=title,
                    message=msg,
                    buttons=3,  # Yes, NO
                    type=QUERYBOX,
                ).execute()
                if result == 2:
                    # yes has been clicked
                    if self._uninstall_items():
                        title = self.dialog_handler._resource_resolver.resolve_string("mbtitle017")
                        msg = self.dialog_handler._resource_resolver.resolve_string("mbmsg019")
                        _ = MessageDialog(
                            self.dialog_handler.ctx,
                            title=title,
                            message=msg,
                            type=INFOBOX,
                        ).execute()
                    else:
                        title = self.dialog_handler._resource_resolver.resolve_string("msg01")
                        msg = self.dialog_handler._resource_resolver.resolve_string("mbmsg020")
                        _ = MessageDialog(
                            self.dialog_handler.ctx,
                            title=title,
                            message=msg,
                            type=ERRORBOX,
                        ).execute()
                    self._log.debug("ButtonListener.actionPerformed: UninstallItems")

        except Exception as err:
            self._log.error(f"ButtonListener.actionPerformed: {err}", exc_info=True)
            raise err

    def _uninstall_items(self) -> bool:
        try:
            from ...install.install_pkg import InstallPkg

            installer = InstallPkg(self.dialog_handler.ctx, flag_upgrade=False)
            success = True
            self._log.debug("_uninstall_items() uninstall_pkgs: %s", self.dialog_handler.uninstall_pkgs)
            for item in self.dialog_handler.uninstall_pkgs:
                try:
                    success = success and installer.uninstall(item, remove_tracking_file=True)
                except Exception as e:
                    self._log.error("_uninstall_items(): %s", e, exc_info=True)
                    success = False
            self.dialog_handler.uninstall_pkgs.clear()
            return success
        except Exception as e:
            self._log.error("_uninstall_items(): %s", e, exc_info=True)
        return False


class CheckBoxUninstallListener(XPropertyChangeListener, unohelper.Base):
    def __init__(self, handler: "OptionsDialogUninstallHandler") -> None:
        XPropertyChangeListener.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("__init__")
        self.handler = handler
        self._config = BasicConfig()
        self._log.debug("__init__ done")

    def disposing(self, Source: Any) -> None:  # noqa: ANN401, N803
        pass

    def propertyChange(self, evt: PropertyChangeEvent) -> None:  # noqa: N802
        self._log.debug("propertyChange")
        try:
            src = cast("UnoControlCheckBoxModel", evt.Source)
            # self._log.debug("propertyChange() checkbox %s", pformat(dir(src)))
            # self._log.debug("propertyChange() checkbox %s", str(src))
            # state (evn.NewValue) will be 1 for true and 0 for false
            state = self.handler.state_to_bool(cast(int, (evt.NewValue)))
            self._log.debug("propertyChange() checkbox %s state: %s", src.Label, state)
            if state:
                self.handler._uninstall_pkgs.add(src.Label)
            else:
                self.handler._uninstall_pkgs.discard(src.Label)
        except Exception as err:
            self._log.error("propertyChange: %s", err, exc_info=True)
            raise


class OptionsDialogUninstallHandler(DialogBase, XContainerWindowEventHandler, unohelper.Base):
    IMPLE_NAME = f"{BasicConfig().lo_implementation_name}.OptUninstallPage"
    SERVICE_NAMES = (IMPLE_NAME,)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        DialogBase.__init__(self, ctx)
        XContainerWindowEventHandler.__init__(self)
        unohelper.Base.__init__(self)
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug("__init__")
        self.ctx = ctx
        self._uninstall_pkgs = set()
        self._config = BasicConfig()
        self._resource_resolver = ResourceResolver(self.ctx)
        self._window_name = "uninstall"  # uninstall.xdl file name
        self._settings = Settings()
        self._window = None
        # these are the factors to convert Dialog units to whatever units that are being used by size and pos.
        self._y_factor = 2.120689655
        self._x_factor = 2.376811594
        self._width_factor = 2.365853658
        self._height_factor = 2.125
        self._current_y = 0
        self._logger.debug("__init__ done")

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region XContainerWindowEventHandler
    def callHandlerMethod(  # type: ignore  # noqa: N802
        self,
        xWindow: UnoControlDialog,  # noqa: N803
        EventObject: Any,  # noqa: ANN401, N803
        MethodName: str,  # noqa: ANN401, N803
    ) -> bool:  # type: ignore
        self._logger.debug("callHandlerMethod: %s", MethodName)
        if MethodName == "external_event":
            try:
                return self._handle_external_event(xWindow, EventObject)
            except Exception as e:
                print(e)
        return True

    def getSupportedMethodNames(self) -> Tuple[str, ...]:  # noqa: N802
        return ("external_event",)

    # endregion XContainerWindowEventHandler

    def _handle_external_event(self, window: UnoControlDialog, ev_name: str) -> bool:
        self._logger.debug("_handle_external_event: %s", ev_name)
        if ev_name == "ok":
            self._save_data(window)
        elif ev_name == "back":
            self._load_data(window, "back")
        elif ev_name == "initialize":
            self._load_data(window, "initialize")
        return True

    def _save_data(self, window: UnoControlDialog) -> None:
        pass

    def _load_data(self, window: UnoControlDialog, ev_name: str) -> None:
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug("_load_data name: %s", name)
        self._logger.debug("_load_data ev_name: %s", ev_name)
        if name != self._window_name:
            self._logger.debug("_load_data: name does not match")
            return
        try:
            self._window = window
            if ev_name == "initialize":
                self._add_package_checks()

                btn = self.create_button(
                    "UninstallItems",
                    self.resource_resolver.resolve_string("uninstall02"),
                    x=138,
                    y=self._current_y,
                    width=60,
                    height=16,
                )
                # self._logger.debug("_load_data: UninstallItems button created %s", str(btn))
                # self._logger.debug("_load_data: UninstallItems button dir %s", pformat(dir(btn.getModel())))
                # self._logger.debug("btn size pos: %s", str(btn.getPosSize()))
                # self._logger.debug("btn after resize, size pos: %s", str(btn.getPosSize()))
                btn_listener = ButtonUninstallListener(self)
                btn.setActionCommand("UninstallItems")
                btn.addActionListener(btn_listener)
                btn_model = btn.getModel()
                btn_model.HelpText = self.resource_resolver.resolve_string("uninstall02")  # type: ignore

                lbl = cast("UnoControlButton", window.getControl("lblUninstall"))
                model = lbl.Model  # type: ignore
                model.Label = self._resource_resolver.resolve_string(model.Label)

        except Exception as err:
            self._logger.error("_load_data(): %s", err, exc_info=True)
            raise err
        return

    def _add_package_checks(self) -> None:
        from ...install.py_packages.packages import Packages
        pkgs = Packages()
        all_pkgs = pkgs.get_all_packages(all_pkg=True)
        names = sorted({pkg.name for pkg in all_pkgs})

        self._current_y = 24
        chk_listener = CheckBoxUninstallListener(self)
        uninstall_str = self._resource_resolver.resolve_string("uninstall02")
        for name in names:
            try:
                chk = self.create_checkbox(f"chk{name.replace('-', '_')}", name, y=self._current_y)
                chk_model = chk.getModel()
                chk_model.addPropertyChangeListener("State", chk_listener)  # type: ignore
                chk_model.HelpText = f"{uninstall_str} {name}"  # type: ignore
                self._current_y += 12
            except Exception as e:
                self._logger.error("_add_package_checks() unable to add %s. %s", name, e, exc_info=True)
                raise

    def state_to_bool(self, state: int) -> bool:
        return bool(state)

    def bool_to_state(self, value: bool) -> int:
        return int(value)

    # region Control Methods
    def create_button(
        self,
        name: str,
        label: str,
        x: int = -1,
        y: int = -1,
        width: int = -1,
        height: int = -1,
        **props: Any,  # noqa: ANN401
    ) -> UnoControlButton:
        if self._window is None:
            raise Exception("Window is not initialized")
        model = self.create("com.sun.star.awt.UnoControlButtonModel")
        model.setPropertyValue("Label", label)
        uno_any = uno.Any("short", STANDARD)  # type: ignore
        uno.invoke(model, "setPropertyValue", ("PushButtonType", uno_any))  # type: ignore
        model.setPropertyValue("Name", name)
        # set any extra user properties
        for k, v in props.items():
            model.setPropertyValue(k, v)

        container = self._window.getModel()
        container.insertByName(name, model)  # type: ignore
        result = cast("UnoControlButton", self._window.getControl(name))  # type: ignore
        self._set_size_pos(result, x=x, y=y, width=width, height=height)
        return result

    def create_checkbox(
        self,
        name: str,
        label: str,
        x: int = 17,
        y: int = -1,
        width: int = 198,
        height: int = 8,
        **props: Any,  # noqa: ANN401
    ) -> UnoControlCheckBox:
        if self._window is None:
            raise Exception("Window is not initialized")
        model = self.create("com.sun.star.awt.UnoControlCheckBoxModel")
        model.setPropertyValue("Label", label)
        model.setPropertyValue("Name", name)
        # set any extra user properties
        for k, v in props.items():
            model.setPropertyValue(k, v)

        container = self._window.getModel()
        container.insertByName(name, model)  # type: ignore
        result = cast("UnoControlCheckBox", self._window.getControl(name))  # type: ignore
        self._set_size_pos(result, x=x, y=y, width=width, height=height)
        return result

    def _set_size_pos(self, ctl: Any, x: int = -1, y: int = -1, width: int = -1, height: int = -1) -> None:  # noqa: ANN401
        """
        Set Position and size for a control.

        |lo_safe|

        Args:
            ctl (XWindow): Control that implements XWindow
            x (int, UnitT, optional): X Position. Defaults to -1.
            y (int, UnitT, optional): Y Position. Defaults to -1.
            width (int, UnitT, optional): Width. Defaults to -1.
            height (int, UnitT, optional): Height. Defaults to -1.
        """

        def get_factor_x(x: int) -> int:
            if x == 0:
                return 0
            return int(x * self._x_factor)

        def get_factor_y(y: int) -> int:
            if y == 0:
                return 0
            return int(y * self._y_factor)

        def get_factor_width(width: int) -> int:
            if width == 0:
                return 0
            return int(width * self._width_factor)

        def get_factor_height(height: int) -> int:
            if height == 0:
                return 0
            return int(height * self._height_factor)

        if x < 0 and y < 0 and width < 0 and height < 0:
            return

        pos_size = None
        if x > -1 and y > -1 and width > -1 and height > -1:
            pos_size = PosSize.POSSIZE
        elif x > -1 and y > -1:
            pos_size = PosSize.POS
        elif width > -1 and height > -1:
            pos_size = PosSize.SIZE
        if pos_size is not None:
            f_x = get_factor_x(x)
            f_y = get_factor_y(y)
            f_width = get_factor_width(width)
            f_height = get_factor_height(height)
            ctl.setPosSize(f_x, f_y, f_width, f_height, pos_size)

    # endregion Control Methods

    @property
    def resource_resolver(self) -> ResourceResolver:
        return self._resource_resolver

    @property
    def uninstall_pkgs(self) -> Set[str]:
        return self._uninstall_pkgs
