from __future__ import annotations
import os
import sys
from abc import abstractmethod
import platform
import subprocess
from pathlib import Path
from typing import Any, List, Dict


from ...config import Config
from ...oxt_logger import OxtLogger
from ..download import Download
from ...lo_util.resource_resolver import ResourceResolver

IS_WIN = platform.system() == "Windows"

# https://stackoverflow.com/search?q=%5Bpython%5D+run+subprocess+without+popup+terminal
# silent subprocess on Windows
# Check for windows
if IS_WIN:
    STARTUP_INFO = subprocess.STARTUPINFO()  # type: ignore
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
else:
    STARTUP_INFO = None


class BaseInstaller:
    """class for the PIP install."""

    def __init__(self, ctx: Any) -> None:
        self.ctx = ctx
        self._config = Config()
        self._logger = self._get_logger()
        self.path_python = self._config.python_path
        self._logger.debug(f"Python path: {self.path_python}")
        self._download = Download()
        self._resource_resolver = ResourceResolver(ctx=self.ctx)

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    @abstractmethod
    def install_pip(self) -> None:
        pass

    def _get_pip_cmd(self, filename: Path) -> List[str]:
        if self._config.is_user_installed:
            cmd = [str(self.path_python), f"{filename}", "--user"]
        else:
            cmd = [str(self.path_python), f"{filename}"]
        return cmd

    def _install_pip(self, filename: Path):
        self._logger.info("Starting PIP installation…")
        try:
            cmd = self._get_pip_cmd(filename=filename)
            if STARTUP_INFO:
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env(), startupinfo=STARTUP_INFO
                )
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env())
            _, stderr = process.communicate()
            str_stderr = stderr.decode("utf-8")
            if process.returncode != 0:
                # "PIP installation has failed, see log"
                self._logger.error("PIP installation has failed")
                if str_stderr:
                    self._logger.error(str_stderr)
                return False
        except Exception as err:
            # "PIP installation has failed, see log"
            self._logger.error("PIP installation has failed")
            self._logger.error(err)
            return False
        return True

    def _get_env(self) -> Dict[str, str]:
        """
        Gets Environment used for subprocess.
        """
        my_env = os.environ.copy()
        py_path = ""
        p_sep = ";" if IS_WIN else ":"
        for d in sys.path:
            py_path = py_path + d + p_sep
        my_env["PYTHONPATH"] = py_path
        return my_env

    def install_requirements(self, fnm: str | Path) -> None:
        """Install the requirements."""
        self._logger.info("install_requirements - Installing requirements…")
        if not self.is_pip_installed():
            self.install_pip()
        if not self.is_pip_installed():
            self._logger.error("install_requirements - PIP installation has failed")
            return
        self._install(path=str(fnm))
        return

    def install_package(self, value: str) -> None:
        """Install a package."""
        if not self.is_pip_installed():
            self.install_pip()
        if not self.is_pip_installed():
            return
        self._install(value=value)
        return

    def pip_upgrade(self) -> None:
        """Upgrade PIP."""
        self._logger.info("pip_upgrade - Upgrading PIP…")
        if not self.is_pip_installed():
            self.install_pip()
        if not self.is_pip_installed():
            return
        self._install()
        return

    def _cmd_pip(self, *args: str) -> List[str]:
        cmd: List[str] = [str(self.path_python), "-m", "pip", *args]
        return cmd

    def _install(self, value: str = "", path: str = ""):
        cmd = ["install", "--upgrade", "--user"]
        msg = "Install - Upgrading pip success!"
        err_msg = "Install - Upgrading pip failed!"
        if value:
            name = value.split()[0].strip()
            cmd = self._cmd_pip(*[*cmd, *name])
            msg = f"Install - Installing {name} success!"
            err_msg = f"Install - Installing {name} failed!"
        else:
            cmd = self._cmd_pip(*[*cmd, "-r", f"{path}"])
            msg = "Install - Installing requirements success!"
            err_msg = "Install - Installing requirements failed!"
        if STARTUP_INFO:
            process = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env(), startupinfo=STARTUP_INFO
            )  # noqa: E501
        else:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env())
        if process.returncode == 0:
            self._logger.info(msg)
        else:
            self._logger.error(err_msg)
        return

    def is_pip_installed(self) -> bool:
        """Check if PIP is installed."""
        # cmd = self._cmd_pip("--version")
        # cmd = '"{}" -m pip -V'.format(self.path_python)
        cmd = [str(self.path_python), "-m", "pip", "-V"]
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

    @property
    def resource_resolver(self) -> ResourceResolver:
        """Gets the resource resolver."""
        return self._resource_resolver

    @property
    def config(self) -> Config:
        """Gets the config."""
        return self._config
