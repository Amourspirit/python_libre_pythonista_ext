from __future__ import annotations
from pathlib import Path
import os
import sys
import subprocess
from typing import List

from ..config import Config


# silent subprocess for Windows
if os.name == "nt":
    _si = subprocess.STARTUPINFO()
    _si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    _si = None


class PipInstallBuild:
    """Install pip packages into Build pythonpath folder."""

    def __init__(self, pkg_name: str, pkg_ver: str) -> None:
        self._config = Config()
        self.path_python = Path(sys.executable)
        self._pkg_name = pkg_name
        self._pkg_ver = pkg_ver
        self._build_path = self._config.root_path / self._config.build_dir_name
        if self._config.zip_preinstall_pure:
            self._pythonpath = self._build_path / "pure"
        else:
            self._pythonpath = self._build_path / "pythonpath"
        self._pythonpath.mkdir(parents=True, exist_ok=True)

    def _cmd_pip(self, *args: str) -> List[str]:
        # pip install --target=d:\somewhere\other\than\the\default package_name
        cmd: List[str] = [str(self.path_python), "-m", "pip", *args]
        return cmd

    def _install_pkg(self, pkg: str, ver: str) -> None:
        """
        Install a package.

        Args:
            pkg (str): The name of the package to install.
            ver (str): The version of the package to install.
        """
        # sourcery skip: raise-specific-error
        target = str(self._pythonpath)
        if " " in target:
            target = f'"{target}"'
        cmd = ["install", f"--target={target}"]

        pkg_cmd = f"{pkg}{ver}" if ver else pkg
        cmd = self._cmd_pip(*[*cmd, pkg_cmd])
        # msg = f"Pip Install - Upgrading success for: {pkg_cmd}"
        err_msg = f"Pip Install - Upgrading failed for: {pkg_cmd}"
        if _si:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=_si)
        else:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise Exception(err_msg)
        return

    def install(self) -> None:
        """Install the package."""
        self._install_pkg(self._pkg_name, self._pkg_ver)
        return
