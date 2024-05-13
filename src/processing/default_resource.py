from __future__ import annotations
import os
import sys
import shutil
from typing import Set, cast, List
from pathlib import Path

import toml
from ..meta.singleton import Singleton
from ..config import Config
from .. import file_util


class DefaultResource(metaclass=Singleton):
    """Singleton Class the Packages."""

    def __init__(self) -> None:
        self._config = Config()
        self._res_path = self._config.build_path / self._config.resource_dir_name
        default_locale = [""] + self._config.default_locale[:]

        self._default_property_file = (
            self._res_path / f"{self._config.resource_properties_prefix}{'_'.join(default_locale)}.default"
        )

    # region Methods

    def ensure_default(self) -> None:
        """Ensure the default resource file exists."""
        # creates a file such as resources/pipstrings_en_US.default
        if not self._default_property_file.exists():
            self._default_property_file.touch()

    # endregion Properties
