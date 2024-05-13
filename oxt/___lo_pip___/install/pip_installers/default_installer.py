from __future__ import annotations

import tempfile
from pathlib import Path

from ...config import Config
from ...oxt_logger import OxtLogger
from ..download import Download

from .base_installer import BaseInstaller
from ..progress import Progress


class DefaultInstaller(BaseInstaller):
    """class for the PIP install."""

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    def install_pip(self) -> None:
        if not self.is_internet:
            self._logger.error("No internet connection")
            return
        pip_installed = False
        cfg = Config()
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
            with tempfile.TemporaryDirectory() as temp_dir:
                # Do something with the temporary directory
                # print(f"Temporary directory created at {temp_dir}")
                path_pip = Path(temp_dir)

                url = cfg.url_pip
                filename = path_pip / "get-pip.py"
                dl = Download()
                data, _, err = dl.url_open(url, verify=False)
                if err:
                    self._logger.error("Unable to download PIP installation file")
                    return
                dl.save_binary(pth=filename, data=data)

                if filename.exists():
                    self._logger.info("PIP installation file has been saved")
                else:
                    self._logger.error("Unable to copy PIP installation file")
                    return

                # PIP installation file has been saved

                try:
                    # "Starting PIP installation…"
                    if self._install_pip(filename=filename) and self.is_pip_installed():
                        self._logger.info("PIP was installed successfully")
                        pip_installed = True
                        return
                except Exception as err:
                    # "PIP installation has failed, see log"
                    self._logger.error(err)
        finally:
            if progress:
                self._logger.debug("Ending Progress Window")
                progress.kill()

        if not pip_installed:
            self._logger.error("PIP installation has failed")

        return
