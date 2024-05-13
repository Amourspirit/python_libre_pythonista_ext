from __future__ import annotations
from typing import List
import sys
import subprocess
from pathlib import Path

from ...config import Config
from ...oxt_logger import OxtLogger
from .base_installer import BaseInstaller
from ..progress import Progress


class FlatpakInstaller(BaseInstaller):
    """Class for the Flatpak PIP install."""

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    def install_pip(self) -> None:
        if self.is_pip_installed():
            self._logger.info("PIP is already installed")
            return
        if not self.is_internet:
            self._logger.error("No internet connection")
            return
        if self._install_wheel():
            if self.is_pip_installed():
                self._logger.info("PIP was installed successfully")
        else:
            self._logger.error("PIP installation has failed")

        return

    def _get_pip_cmd(self, filename: Path) -> List[str]:
        return [str(self.path_python), f"{filename}", "--user"]

    def _install_wheel(self) -> bool:
        cfg = Config()
        result = False
        from ..install_pip_from_wheel import InstallPipFromWheel

        installer = InstallPipFromWheel(ctx=self.ctx)
        progress: Progress | None = None
        if cfg.show_progress:
            self._logger.debug("Starting Progress Window")
            msg = self.resource_resolver.resolve_string("msg08")
            title = self.resource_resolver.resolve_string("title01") or self.config.lo_implementation_name
            progress = Progress(start_msg=f"{msg} PIP", title=title)
            progress.start()
        else:
            self._logger.debug("Progress Window is disabled")

        try:
            installer.install(cfg.site_packages)
            if cfg.site_packages not in sys.path:
                sys.path.append(cfg.site_packages)
            result = True
        except Exception as err:
            self._logger.error(err)
            return result
        finally:
            if progress:
                self._logger.debug("Ending Progress Window")
                progress.kill()
        return result

    def _install_pip(self, filename: Path):
        self._logger.info("Starting PIP installation…")
        cfg = Config()
        try:
            cmd = self._get_pip_cmd(filename)
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
