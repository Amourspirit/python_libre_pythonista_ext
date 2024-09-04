from __future__ import annotations
import os
from pathlib import Path
import site
from typing import Dict, cast, TypedDict
import json
import platform
from ..config import Config


class B2ZItemT(TypedDict):
    url: str
    md5: str


class ConfigMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            root = Path(__file__).parent
            config_file = Path(root, "bz2_config.json")
            with open(config_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            cls._instance = super().__call__(**data)
        return cls._instance


class BZ2Config(metaclass=ConfigMeta):
    """
    Singleton Class. bz2 Config.

    This class is for Windows only.
    """

    def __init__(self, **kwargs) -> None:
        """Constructor"""
        self._32_bit = cast(Dict[str, B2ZItemT], kwargs["32_bit"])
        self._64_bit = cast(Dict[str, B2ZItemT], kwargs["64_bit"])
        self._config = Config()
        # using platform.architecture()[0] works for both 32-bit and 64-bit LIbreOffice.
        # Tested in portable version of LibreOffice and in Windows 10 and it reports 32bit.
        # Tested installed 64 bit version of LibreOffice and in Windows 10 and it reports 64bit.
        self._is_32_bit = platform.architecture()[0] == "32bit"
        # site.USER_BASE is the user base directory, such as 'C:\Users\user\\AppData\\Roaming\Python
        if site.USER_BASE:
            install_dir = Path(site.USER_BASE)
        else:
            install_dir = Path(str(os.getenv("APPDATA"))) / "Roaming/Python"
        bits = "32" if self._is_32_bit else "64"
        self._install_dir = (
            install_dir / f"Python{self._config.python_major_minor.replace('.', '')}/{bits}/site-packages"
        )
        if not self._install_dir.exists():
            self._install_dir.mkdir(parents=True, exist_ok=True)

    def get_config(self) -> B2ZItemT:
        """Gets the bz2 config for the current python version and Operating System."""
        if self._is_32_bit:
            return cast(B2ZItemT, self._32_bit[self._config.python_major_minor])
        else:
            return cast(B2ZItemT, self._64_bit[self._config.python_major_minor])

    @property
    def install_dir(self) -> Path:
        """
        Gets the install directory.

        Such as: C:\\Users\\user\\AppData\\Roaming\\Python\\Python38\\64site-packages
        """
        return self._install_dir
