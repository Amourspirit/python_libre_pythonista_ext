from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
import os
import sys
import subprocess
import uno

from ooodev.loader import Lo
from ooodev.dialog.msgbox import MessageBoxType, MsgBox
from ooodev.dialog.input import Input
from ooodev.globals import GTC


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class PkgInfo:

    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._ctx = Lo.get_context()
        self._rr = ResourceResolver(self._ctx)
        self._config = Config()

    def get_env(self) -> Dict[str, str]:
        """
        Gets Environment used for subprocess.
        """
        cache = GTC()
        key = f"{self.__class__.__module__}.py_subprocess_env"
        if key in cache:
            if self._log.is_debug:
                self._log.debug(f"Cache hit: {key}")
            return cache[key]
        my_env = os.environ.copy()
        py_path = ""
        p_sep = ";" if os.name == "nt" else ":"
        for d in sys.path:
            py_path = py_path + d + p_sep
        my_env["PYTHONPATH"] = py_path
        cache[key] = my_env
        return my_env

    def get_cmd_pip(self, *args: str) -> List[str]:
        """
        Gets the command to run pip in a subprocess.

        Returns:
            List[str]: Command to run pip.
        """
        cmd: List[str] = [str(self._config.python_path), "-m", "pip", *args]
        if self._config.log_pip_installs and self._config.log_file:
            log_file = self._config.log_file

            if " " in log_file:
                log_file = f'"{log_file}"'
            cmd.append(f"--log={log_file}")
        return cmd

    def is_package_installed(self, pkg_name: str) -> bool:
        """Check if a package is installed."""
        result = subprocess.run(
            self.get_cmd_pip("show", pkg_name),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.get_env(),
        )
        return result.returncode == 0

    def show_installed(self) -> None:
        """Install pip packages."""
        self._log.debug("InstallPipPkg.show_installed()")
        pkg_name = Input.get_input(
            title=self._rr.resolve_string("strPackageName"),
            msg=self._rr.resolve_string("strPackageNameInstallChk"),
            ok_lbl=self._rr.resolve_string("dlg01"),
            cancel_lbl=self._rr.resolve_string("dlg02"),
        )
        self._log.debug(f"show_installed() Package name: {pkg_name}")
        pkg_name = pkg_name.strip()
        if not pkg_name:
            self._log.debug("show_installed() No input.")
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg008"),
                title=self._rr.resolve_string("mbtitle008"),
                boxtype=MessageBoxType.INFOBOX,
            )
            return

        if self.is_package_installed(pkg_name):
            if ver := self.get_package_version(pkg_name):
                msg = self._rr.resolve_string("mbmsg011").format(pkg_name, ver)  # Package {} version {} is installed
            else:
                msg = self._rr.resolve_string("mbmsg009").format(pkg_name)  # Package {} is installed
            MsgBox.msgbox(
                msg,  # Package {} is installed
                title=self._rr.resolve_string("title02"),
                boxtype=MessageBoxType.INFOBOX,
            )
            self._log.info(f"Package {pkg_name} is installed.")
        else:
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg010").format(pkg_name),  # Package {} is not installed
                title=self._rr.resolve_string("title02"),
                boxtype=MessageBoxType.INFOBOX,
            )
            self._log.info(f"Package {pkg_name} is not installed.")

    def get_package_version(self, pkg_name: str) -> str:
        result = subprocess.run(
            self.get_cmd_pip("show", pkg_name),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.get_env(),
        )
        if result.returncode != 0:
            return ""

        return next(
            (line.split(":", 1)[1].strip() for line in result.stdout.splitlines() if line.startswith("Version:")),
            "",
        )
