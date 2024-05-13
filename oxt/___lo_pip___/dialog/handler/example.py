from __future__ import annotations
from typing import Any, TYPE_CHECKING, cast
import uno
import unohelper

from com.sun.star.awt import XActionListener
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.ui.dialogs.TemplateDescription import FILESAVE_AUTOEXTENSION, FILEOPEN_SIMPLE  # type: ignore

from ...basic_config import BasicConfig
from ...lo_util.resource_resolver import ResourceResolver

from ...lo_util.configuration import Configuration, SettingsT
from ...settings.settings import Settings
from ..file_open_dialog import FileOpenDialog

from ...oxt_logger import OxtLogger

if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlEdit  # service
    from com.sun.star.awt import UnoControlButton  # service


IMPLEMENTATION_NAME = f"{BasicConfig().lo_implementation_name}.Example"


class ButtonListener(unohelper.Base, XActionListener):
    def __init__(self, cast: "OptionsDialogHandler"):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("ButtonListener.__init__")
        self.cast = cast
        self._logger.debug("ButtonListener.__init__ done")

    def disposing(self, ev: Any):
        pass

    def actionPerformed(self, ev: Any):
        self._logger.debug("ButtonListener.actionPerformed")
        try:
            cmd = str(ev.ActionCommand)
            self._logger.debug(f"ButtonListener.actionPerformed cmd: {cmd}")
            if cmd == "ChooseEditor":
                if ret := self.cast.choose_file():
                    path = uno.fileUrlToSystemPath(ret)
                    ev.Source.getContext().getControl("txtTest").setText(path)
        except Exception as err:
            self._logger.error(f"ButtonListener.actionPerformed: {err}", exc_info=True)
            raise err


class OptionsDialogHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx: Any):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("OptionsDialogHandler.__init__")
        self.ctx = ctx
        self._config = BasicConfig()
        self._resource_resolver = ResourceResolver(self.ctx)
        self._config_node = f"/{self._config.lo_implementation_name}.Settings/Logging"
        self._window_name = "example"
        self._settings = Settings()
        self._logger.debug("OptionsDialogHandler.__init__ done")

    # region XContainerWindowEventHandler
    def callHandlerMethod(self, window: UnoControlDialog, eventObject: Any, method: str):
        self._logger.debug(f"OptionsDialogHandler.callHandlerMethod: {method}")
        if method == "external_event":
            try:
                self._handle_external_event(window, eventObject)
            except Exception as e:
                print(e)
            return True

    def getSupportedMethodNames(self):
        return ("external_event",)

    # endregion XContainerWindowEventHandler

    def _handle_external_event(self, window: UnoControlDialog, ev_name: str):
        self._logger.debug(f"OptionsDialogHandler._handle_external_event: {ev_name}")
        if ev_name == "ok":
            self._save_data(window)
        elif ev_name == "back":
            self._load_data(window, "back")
        elif ev_name == "initialize":
            self._load_data(window, "initialize")
        return True

    def _save_data(self, window: UnoControlDialog):
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug(f"OptionsDialogHandler._save_data name: {name}")
        if name != self._window_name:
            return
        editor = window.getControl("txtTest")
        settings: SettingsT = {
            "names": ("TestText",),
            "values": (editor.Text,),  # type: ignore
        }
        self._logger.debug(f"OptionsDialogHandler._save_data settings: {settings}")
        self._config_writer(settings)

    def _load_data(self, window: UnoControlDialog, ev_name: str):
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug(f"OptionsDialogHandler._load_data name: {name}")
        self._logger.debug(f"OptionsDialogHandler._load_data ev_name: {ev_name}")
        if name != self._window_name:
            return
        try:
            if ev_name == "initialize":
                listener = ButtonListener(self)
                btn_choose = cast("UnoControlButton", window.getControl("btnChoose"))
                # btn_Choose.ActionCommand = "ChooseEditor"
                btn_choose.setActionCommand("ChooseEditor")
                btn_choose.addActionListener(listener)
                for control in window.Controls:  # type: ignore
                    if not control.supportsService("com.sun.star.awt.UnoControlEdit"):
                        model = control.Model
                        model.Label = self._resource_resolver.resolve_string(model.Label)
            if settings := self._settings.current_settings:
                self._logger.debug(f"OptionsDialogHandler._load_data settings TestText: {settings['TestText']}")
                tf_test = cast("UnoControlEdit", window.getControl("txtTest"))
                tf_test.setText(settings["TestText"])
        except Exception as err:
            self._logger.error(f"OptionsDialogHandler._load_data: {err}", exc_info=True)
            raise err
        return

    def _config_writer(self, settings: SettingsT):
        try:
            cfg = Configuration()
            cfg.save_configuration(self._config_node, settings)
        except Exception as e:
            raise e

    def choose_file(self):
        self._logger.debug("OptionsDialogHandler.choose_file")
        try:
            return self._get_file_url()
        except Exception as err:
            self._logger.error(f"OptionsDialogHandler.choose_file: {err}", exc_info=True)
            raise err

    def _get_file_url(self):
        url = FileOpenDialog(
            self.ctx,
            template=FILEOPEN_SIMPLE,
            filters=(
                (self._resource_resolver.resolve_string("ex03"), "*.*"),
                (self._resource_resolver.resolve_string("ex04"), "*.exe;*.bin;*.sh"),
            ),
        ).execute()
        return url or False


# g_ImplementationHelper = unohelper.ImplementationHelper()

# g_ImplementationHelper.addImplementation(
#     OptionsDialogHandler,
#     IMPLEMENTATION_NAME,
#     (IMPLEMENTATION_NAME,),
# )
