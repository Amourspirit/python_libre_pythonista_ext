from __future__ import annotations
import os
import sys
import subprocess
from typing import Any, Dict

from ..config import Config
from ..oxt_logger import OxtLogger
from .download import Download

from .pip_installers.base_installer import STARTUP_INFO


class InstallPip:
    """class for the PIP install."""

    def __init__(self, ctx: Any) -> None:
        self.ctx = ctx
        self._config = Config()
        self._logger = OxtLogger(log_name=__name__)
        self._download = Download()

    def install_pip(self) -> None:
        if self._config.is_flatpak:
            self._logger.info("Flatpak detected, installing PIP via Flatpak installer")
            self._install_flatpak()
        else:
            self._logger.info("Installing PIP via default installer")
            self._install_default()

    def _install_default(self) -> None:
        from .pip_installers.default_installer import DefaultInstaller

        installer = DefaultInstaller(ctx=self.ctx)
        installer.install_pip()

    def _install_flatpak(self) -> None:
        from .pip_installers.flatpak_installer import FlatpakInstaller

        installer = FlatpakInstaller(ctx=self.ctx)
        installer.install_pip()

    def _get_env(self) -> Dict[str, str]:
        """
        Gets Environment used for subprocess.
        """
        my_env = os.environ.copy()
        py_path = ""
        p_sep = ";" if self._config.is_win else ":"
        for d in sys.path:
            py_path = py_path + d + p_sep
        my_env["PYTHONPATH"] = py_path
        return my_env

    def is_pip_installed(self) -> bool:
        """Check if PIP is installed."""
        # cmd = self._cmd_pip("--version")
        # cmd = '"{}" -m pip -V'.format(self.path_python)
        cmd = [str(self._config.python_path), "-m", "pip", "-V"]
        if STARTUP_INFO:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env(), startupinfo=STARTUP_INFO
            )
        else:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env())
        return result.returncode == 0

    @property
    def is_internet(self) -> bool:
        """Gets if there is an internet connection."""
        return self._download.is_internet
