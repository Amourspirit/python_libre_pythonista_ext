from __future__ import annotations
from typing import Any, TYPE_CHECKING, cast
from pathlib import Path
import sys
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.beans import XPropertyChangeListener
from com.sun.star.beans import PropertyChangeEvent  # struct


if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlCheckBox
    from com.sun.star.awt import UnoControlCheckBoxModel

    from ....___lo_pip___.config import Config
    from ....___lo_pip___.basic_config import BasicConfig
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ....___lo_pip___.lo_util.configuration import Configuration, SettingsT
    from ....___lo_pip___.settings.settings import Settings
    from ....___lo_pip___.oxt_logger import OxtLogger
    from ....___lo_pip___.dialog.message_dialog import MessageDialog
else:

    def add_local_path_to_sys_path():
        """Add the local path to sys.path."""

        def find_root_path(current_path) -> str:
            if current_path == Path("/"):
                return ""
            if (current_path / "___lo_pip___").exists():
                return str(current_path)
            return find_root_path(current_path.parent)

        root_path = find_root_path(Path(__file__).parent)
        if not root_path:
            return
        if root_path not in sys.path:
            sys.path.append(root_path)

    add_local_path_to_sys_path()

    from ___lo_pip___.basic_config import BasicConfig
    from ___lo_pip___.config import Config
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.lo_util.configuration import Configuration, SettingsT
    from ___lo_pip___.settings.settings import Settings
    from ___lo_pip___.oxt_logger import OxtLogger
    from ___lo_pip___.dialog.message_dialog import MessageDialog


# IMPLEMENTATION_NAME = f"{BasicConfig().lo_implementation_name}.LoggingOptionsPage"


class CheckBoxListener(XPropertyChangeListener, unohelper.Base):
    def __init__(self, cast: "SettingsDialogHandler"):
        XPropertyChangeListener.__init__(self)
        unohelper.Base.__init__(self)
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug("__init__")
        self.cast = cast
        self._logger.debug("__init__ done")

    def disposing(self, Source: Any):
        pass

    def propertyChange(self, evt: PropertyChangeEvent):
        self._logger.debug("propertyChange")
        try:
            # state (evn.NewValue) will be 1 for true and 0 for false
            src = cast("UnoControlCheckBoxModel", evt.Source)
            self.cast.use_experimental_editor = src.State == 1  # checked
        except Exception as err:
            self._logger.error("propertyChange: %s", err, exc_info=True)
            raise


class SettingsDialogHandler(XContainerWindowEventHandler, unohelper.Base):
    IMPLE_NAME = f"{BasicConfig().lo_implementation_name}.LpOptionsPage"
    SERVICE_NAMES = (IMPLE_NAME,)

    def __init__(self, ctx: Any):
        XContainerWindowEventHandler.__init__(self)
        unohelper.Base.__init__(self)
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug("__init__")
        self.ctx = ctx
        self._config = Config()
        self._resource_resolver = ResourceResolver(self.ctx)
        self._config_node = (
            f"/{self._config.lo_implementation_name}.Settings/LpSettings"
        )
        self._window_name = "settings"
        self._use_experimental_editor = False
        self._use_experimental_editor_orig = False
        self._settings = Settings()
        self._logger.debug("__init__ done")

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region XContainerWindowEventHandler

    def callHandlerMethod(  # type: ignore
        self, xWindow: UnoControlDialog, EventObject: Any, MethodName: str
    ):
        self._logger.debug("callHandlerMethod: %s", MethodName)
        if MethodName == "external_event":
            try:
                self._handle_external_event(xWindow, EventObject)
            except Exception as e:
                print(e)
            return True

    def getSupportedMethodNames(self):
        return ("external_event",)

    # endregion XContainerWindowEventHandler

    def _has_options_changed(self):
        if self._use_experimental_editor != self._use_experimental_editor_orig:
            return True
        return False

    def _handle_external_event(self, window: UnoControlDialog, ev_name: str):
        self._logger.debug("_handle_external_event: %s", ev_name)
        if ev_name == "ok":
            self._save_data(window)
        elif ev_name == "back":
            self._load_data(window, "back")
        elif ev_name == "initialize":
            self._load_data(window, "initialize")
        return True

    def _save_data(self, window: UnoControlDialog):
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug("_save_data name: %s", name)
        if name != self._window_name:
            return
        checkbox_experimental_logging = cast(
            "UnoControlCheckBox", window.getControl("chkExperimental")
        )
        self._use_experimental_editor = (
            checkbox_experimental_logging.getState() == 1
        )  # checked
        settings: SettingsT = {
            "names": ("ExperimentalEditor",),
            "values": (self._use_experimental_editor,),  # type: ignore
        }
        self._logger.debug("_save_data settings: %s", settings)
        self._config_writer(settings)
        if self._has_options_changed():
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
                self._logger.error("_save_data: %s", err, exc_info=True)

    def _load_data(self, window: UnoControlDialog, ev_name: str):
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug("_load_data name: %s", name)
        self._logger.debug("_load_data ev_name: %s", ev_name)
        if name != self._window_name:
            return
        try:
            if ev_name == "initialize":
                chk_box_listen = CheckBoxListener(self)
                chk_experimental = cast(
                    "UnoControlCheckBox", window.getControl("chkExperimental")
                )
                chk_experimental_model = cast(
                    "UnoControlCheckBoxModel", chk_experimental.getModel()
                )
                chk_experimental_model.addPropertyChangeListener(
                    "State", chk_box_listen
                )
                chk_experimental_model.Label = self._resource_resolver.resolve_string(
                    chk_experimental_model.Label
                )

                settings = self._settings.current_settings
                if settings:
                    if self._logger.is_debug:
                        self._logger.debug("_load_data settings: %s", settings)
                    self._use_experimental_editor_orig = cast(
                        bool, settings["ExperimentalEditor"]
                    )

                    self._use_experimental_editor = self._use_experimental_editor_orig
                    self._logger.debug(
                        "_load_data settings ExperimentalEditor: %s",
                        self._use_experimental_editor,
                    )
                    if self._use_experimental_editor:
                        chk_experimental_model.State = 1
                    else:
                        chk_experimental_model.State = 0
            else:
                self._logger.error("_load_data: settings is None")

        except Exception as err:
            self._logger.error("._load_data: %s", err, exc_info=True)
            raise err
        return

    def _config_writer(self, settings: SettingsT):
        try:
            cfg = Configuration()
            cfg.save_configuration(self._config_node, settings)
        except Exception as e:
            raise e

    @property
    def use_experimental_editor(self) -> bool:
        """Gets/Sets if experimental editor is used."""
        return self._use_experimental_editor

    @use_experimental_editor.setter
    def use_experimental_editor(self, value: bool):
        self._use_experimental_editor = value


# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*SettingsDialogHandler.get_imple())

# endregion Implementation
