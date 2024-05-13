from __future__ import annotations
from typing import Any, TYPE_CHECKING, cast
import uno
import unohelper

from com.sun.star.awt import XActionListener
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.beans import XPropertyChangeListener
from com.sun.star.beans import PropertyChangeEvent  # struct

from ...basic_config import BasicConfig
from ...config import Config
from ...lo_util.resource_resolver import ResourceResolver

from ...lo_util.configuration import Configuration, SettingsT
from ...settings.settings import Settings

from ...oxt_logger import OxtLogger
from ..message_dialog import MessageDialog
from ...lo_util.clipboard import copy_to_clipboard

if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlEdit  # service
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlButton  # service
    from com.sun.star.awt import UnoControlRadioButton  # service
    from com.sun.star.awt import UnoControlRadioButtonModel  # service
    from com.sun.star.awt import UnoControlFixedText


IMPLEMENTATION_NAME = f"{BasicConfig().lo_implementation_name}.LoggingOptionsPage"

_LOG_OPTS = {
    "optLogNone": "NONE",
    "optLogDebug": "DEBUG",
    "optLogNormal": "INFO",
    "optLogWarning": "WARNING",
    "optLogError": "ERROR",
    "optLogCritical": "CRITICAL",
}
_OPT_LOG = {
    "NONE": "optLogNone",
    "DEBUG": "optLogDebug",
    "INFO": "optLogNormal",
    "WARNING": "optLogWarning",
    "ERROR": "optLogError",
    "CRITICAL": "optLogCritical",
}


class ButtonListener(unohelper.Base, XActionListener):
    def __init__(self, cast: "OptionsDialogHandler"):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("ButtonListener.__init__")
        self.cast = cast
        self._logger.debug("ButtonListener.__init__ done")

    def disposing(self, ev: Any):
        pass

    def actionPerformed(self, ev: Any):
        # sourcery skip: extract-method
        self._logger.debug("ButtonListener.actionPerformed")
        try:
            cmd = str(ev.ActionCommand)
            self._logger.debug(f"ButtonListener.actionPerformed cmd: {cmd}")
            if cmd == "CopyLogPath":
                window = cast("UnoControlDialog", ev.Source.getContext())
                # lbl_log = cast("UnoControlFixedText", ev.Source.getContext().getControl("lblLogLocation"))
                lbl_log = cast("UnoControlFixedText", window.getControl("lblLogLocation"))
                clip_text = lbl_log.getText()
                copy_to_clipboard(clip_text)
                self._logger.debug(f"Copied to clipboard lbl_log: {clip_text}")
                title = self.cast._resource_resolver.resolve_string("msg04")
                msg = self.cast._resource_resolver.resolve_string("msg05")
                _ = MessageDialog(
                    self.cast.ctx,
                    window.getPeer(),
                    title=title,
                    message=msg,
                ).execute()
        except Exception as err:
            self._logger.error(f"ButtonListener.actionPerformed: {err}", exc_info=True)
            raise err


class RadioButtonListener(unohelper.Base, XPropertyChangeListener):
    def __init__(self, cast: "OptionsDialogHandler"):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("RadioButtonListener.__init__")
        self.cast = cast
        self._logger.debug("RadioButtonListener.__init__ done")

    def disposing(self, ev: Any):
        pass

    def propertyChange(self, ev: PropertyChangeEvent):
        self._logger.debug("RadioButtonListener.propertyChange")
        try:
            # state (evn.NewValue) will be 1 for true and 0 for false
            src = cast("UnoControlRadioButtonModel", ev.Source)
            if src.Name in _LOG_OPTS:
                self.cast.logging_level = _LOG_OPTS[src.Name]
        except Exception as err:
            self._logger.error(f"RadioButtonListener.propertyChange: {err}", exc_info=True)
            raise


class OptionsDialogHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx: Any):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("OptionsDialogHandler.__init__")
        self.ctx = ctx
        self._config = Config()
        self._resource_resolver = ResourceResolver(self.ctx)
        self._config_node = f"/{self._config.lo_implementation_name}.Settings/Logging"
        self._window_name = "logging"
        self._logging_level = "INFO"
        self._logging_level_original = "INFO"
        self._logging_format = ""
        self._logging_format_original = ""
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

    def _has_log_options_changed(self):
        if self._logging_level != self._logging_level_original:
            return True
        return self._logging_format != self._logging_format_original

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
        txt_log_format = cast("UnoControlEdit", window.getControl("txtLogFormat"))
        self._logging_format = txt_log_format.getText()

        settings: SettingsT = {
            "names": ("LogLevel", "LogFormat"),
            "values": (self.logging_level, self._logging_format),  # type: ignore
        }
        self._logger.debug(f"OptionsDialogHandler._save_data settings: {settings}")
        self._config_writer(settings)
        if self._has_log_options_changed():
            try:
                title = self._resource_resolver.resolve_string("msg02")
                msg = self._resource_resolver.resolve_string("msg03")
                _ = MessageDialog(
                    self.ctx,
                    window.getPeer(),
                    title=title,
                    message=msg,
                ).execute()
            except Exception as err:
                self._logger.error(f"OptionsDialogHandler._save_data: {err}", exc_info=True)

    def _load_data(self, window: UnoControlDialog, ev_name: str):
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug(f"OptionsDialogHandler._load_data name: {name}")
        self._logger.debug(f"OptionsDialogHandler._load_data ev_name: {ev_name}")
        if name != self._window_name:
            return
        try:
            if ev_name == "initialize":
                btn_listener = ButtonListener(self)
                btn_choose = cast("UnoControlButton", window.getControl("btnCopy"))
                # btn_Choose.ActionCommand = "ChooseEditor"
                btn_choose.setActionCommand("CopyLogPath")
                btn_choose.addActionListener(btn_listener)

                opt_listener = RadioButtonListener(self)

                for opt in _LOG_OPTS.keys():
                    opt_model = cast("UnoControlRadioButtonModel", window.getControl(opt).getModel())
                    opt_model.addPropertyChangeListener("State", opt_listener)

                for control in window.Controls:  # type: ignore
                    if not control.supportsService("com.sun.star.awt.UnoControlEdit"):
                        model = control.Model
                        model.Label = self._resource_resolver.resolve_string(model.Label)

            if settings := self._settings.current_settings:
                self._logging_level_original = settings["LogLevel"]
                self._logging_level = self._logging_level_original
                self._logger.debug(
                    f"OptionsDialogHandler._load_data settings LogLevel: {self._logging_level_original}"
                )
                if self._logging_level in _OPT_LOG:
                    opt_log = cast("UnoControlRadioButton", window.getControl(_OPT_LOG[self._logging_level]))
                    opt_log.setState(True)

                self._logging_format_original = str(settings["LogFormat"])
                self._logging_format = self._logging_format_original
                txt_log_format = cast("UnoControlEdit", window.getControl("txtLogFormat"))
                txt_log_format.setText(self._logging_format)
            # must come after for control in window.Controls:
            lbl_log = cast("UnoControlFixedText", window.getControl("lblLogLocation"))
            lbl_log.setText(str(self._config.log_file))

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

    @property
    def logging_level(self):
        """Gets/Sets the logging level."""
        return self._logging_level

    @logging_level.setter
    def logging_level(self, value: str):
        self._logging_level = value


# g_ImplementationHelper = unohelper.ImplementationHelper()

# g_ImplementationHelper.addImplementation(
#     OptionsDialogHandler,
#     IMPLEMENTATION_NAME,
#     (IMPLEMENTATION_NAME,),
# )
