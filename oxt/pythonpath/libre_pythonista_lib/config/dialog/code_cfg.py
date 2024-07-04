from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import json

from ...utils.singleton import SingletonMeta

if TYPE_CHECKING:
    from .....___lo_pip___.lo_util.configuration import Configuration, SettingsT
    from .....___lo_pip___.settings.settings import Settings
else:
    from ___lo_pip___.lo_util.configuration import Configuration
    from ___lo_pip___.settings.settings import Settings

    SettingsT = Any


class CodeCfg(metaclass=SingletonMeta):
    # _instance: CodeCfg = None  # type: ignore

    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._is_init = False
    #     return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        settings = Settings()
        # self._configuration = Configuration()
        _ = Configuration()
        self._node_value = f"/{settings.lo_implementation_name}.Settings/LpDialogWindow"
        self._prop_name_code_window = "CodeWindowJson"
        json_str = str(settings.current_settings.get(self._prop_name_code_window, ""))
        if json_str:
            self._cfg = cast(dict, json.loads(json_str))
        else:
            self._cfg = {}
        self._is_init = True

    # region Methods
    def save(self) -> None:
        """
        Saves the configuration to the settings.
        """
        json_str = json.dumps(self._cfg)
        settings: SettingsT = {
            "names": (self._prop_name_code_window,),
            "values": (json_str,),  # type: ignore
        }
        cfg = Configuration()
        cfg.save_configuration(self._node_value, settings)

    def has_size(self) -> bool:
        """
        Determines if the dialog has a size.
        """
        return self.width > 0 and self.height > 0

    def has_position(self) -> bool:
        """
        Determines if the dialog has a position.
        """
        return self.x > -1 and self.y > -1

    # endregion Methods

    # region Properties
    @property
    def width(self) -> int:
        """
        Gets the width of the dialog.
        """
        return self._cfg.get("width", -1)

    @width.setter
    def width(self, value: int) -> None:
        """
        Sets the width of the dialog.
        """
        self._cfg["width"] = value

    @property
    def height(self) -> int:
        """
        Gets the height of the dialog.
        """
        return self._cfg.get("height", -1)

    @height.setter
    def height(self, value: int) -> None:
        """
        Sets the height of the dialog.
        """
        self._cfg["height"] = value

    @property
    def x(self) -> int:
        """
        Gets the x coordinate of the dialog.
        """
        return self._cfg.get("x", -1)

    @x.setter
    def x(self, value: int) -> None:
        """
        Sets the x coordinate of the dialog.
        """
        self._cfg["x"] = value

    @property
    def y(self) -> int:
        """
        Gets the y coordinate of the dialog.
        """
        return self._cfg.get("y", 1)

    @y.setter
    def y(self, value: int) -> None:
        """
        Sets the y coordinate of the dialog.
        """
        self._cfg["y"] = value

    @property
    def menu_bar_height(self) -> int:
        """
        Gets the y coordinate of the dialog.
        """
        return self._cfg.get("mb_height", 26)

    @menu_bar_height.setter
    def menu_bar_height(self, value: int) -> None:
        """
        Sets the y coordinate of the dialog.
        """
        self._cfg["mb_height"] = value

    # endregion Properties
