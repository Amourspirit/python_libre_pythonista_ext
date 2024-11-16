from __future__ import annotations
from typing import cast, TYPE_CHECKING

import uno  # noqa # type: ignore

from .settings import Settings
from ..meta.singleton import Singleton
from ..lo_util.configuration import Configuration

if TYPE_CHECKING:
    from ..lo_util.configuration import SettingsT


class LpSettings(metaclass=Singleton):
    """Singleton Class. Manages LibrePythonista Settings for the extension."""

    def __init__(self) -> None:
        settings = Settings()
        self._configuration = Configuration()
        self._experimental_editor = cast(
            bool, settings.current_settings.get("ExperimentalEditor", False)
        )
        self._node_value = f"/{settings.lo_implementation_name}.Settings/LpSettings"

    @property
    def experimental_editor(self) -> bool:
        """Gets/Sets the installed local pips."""
        return self._experimental_editor

    @experimental_editor.setter
    def experimental_editor(self, value: bool) -> None:
        # settings: SettingsT = {
        #     "names": ("ExperimentalEditor",),
        #     "values": (str(value).lower(),),
        # }
        settings: SettingsT = {
            "names": ("ExperimentalEditor",),
            "values": (value,),
        }

        self._configuration.save_configuration(
            node_value=self._node_value, settings=settings
        )
        self._experimental_editor = value
