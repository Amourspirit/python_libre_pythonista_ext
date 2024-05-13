from __future__ import annotations
from typing import Any
import tempfile
from pathlib import Path

from ..config import Config
from .download import Download
from ..oxt_logger import OxtLogger
from ..input_output import file_util
from .install_pkg import InstallPkg


class InstallPipFromWheel:
    """Download and install PIP from wheel url"""

    def __init__(self, ctx: Any) -> None:
        self.ctx = ctx
        self._config = Config()
        self._logger = OxtLogger(log_name=__name__)

    def install(self, dst: str | Path = "") -> None:
        """
        Install pip from wheel file.

        Downloads the pip wheel file from the url provided in the config file and unzips it to the destination directory.

        Args:
            dst (str | Path, Optional): The destination directory where the pip wheel file will be installed. If not provided, the ``pythonpath`` location will be used.

        Returns:
            None:

        Raises:
            None:
        """
        url = self._config.pip_wheel_url
        if not url:
            self._logger.error("PIP installation has failed - No wheel url")
            return

        if not self.is_internet:
            self._logger.error("No internet connection!")
            return

        if not dst:
            root_pth = Path(file_util.get_package_location(self._config.lo_identifier))
            dst = root_pth / "pythonpath"

        with tempfile.TemporaryDirectory() as temp_dir:
            # temp_dir = tempfile.gettempdir()
            path_pip = Path(temp_dir)

            filename = path_pip / "pip-wheel.whl"

            dl = Download()
            data, _, err = dl.url_open(url, verify=False)
            if err:
                self._logger.error("Unable to download PIP installation wheel file")
                return
            dl.save_binary(pth=filename, data=data)

            if filename.exists():
                self._logger.info("PIP wheel file has been saved")
            else:
                self._logger.error("PIP wheel file has not been saved")
                return

            try:
                self._unzip_wheel(filename=filename, dst=dst)
            except Exception:
                return
            # now that pip has been installed from wheel force a reinstall to ensure it is the latest version
            self._force_install_pip()

    def _unzip_wheel(self, filename: Path, dst: str | Path) -> None:
        """Unzip the downloaded wheel file"""
        # sourcery skip: raise-specific-error
        if isinstance(dst, str):
            dst = Path(dst)
        try:
            file_util.unzip_file(filename, dst)
            if dst.exists():
                self._logger.debug(f"PIP wheel file has been unzipped to {dst}")
            else:
                self._logger.error("PIP wheel file has not been unzipped")
                raise Exception("PIP wheel file has not been unzipped")
        except Exception as err:
            self._logger.error(f"Unable to unzip wheel file: {err}", exc_info=True)
            raise

    def _force_install_pip(self) -> None:
        """Now that pip has been installed, force reinstall it to ensure it is the latest version"""
        installer = InstallPkg(ctx=self.ctx)
        ver = installer.get_package_version("pip")
        if ver:
            ver = f">={ver}"

        installer.install(req={"pip": ver}, force=True)

    @property
    def is_internet(self) -> bool:
        """Gets if there is an internet connection."""
        try:
            return self._is_internet
        except AttributeError:
            self._is_internet = Download().is_internet
            return self._is_internet
