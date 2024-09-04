from __future__ import annotations
from typing import Any
import tempfile
import hashlib
import shutil
from pathlib import Path

from ...bz2_config.bz2_config import BZ2Config
from ...input_output import file_util
from ...oxt_logger import OxtLogger
from ..download import Download
from ..pip_installers.base_installer import BaseInstaller
from ..progress import Progress


class BZ2Install(BaseInstaller):
    """Install bz2"""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx=ctx)
        self._bz2_config = BZ2Config()

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    def needs_install(self) -> bool:
        """Check if needs install"""
        if not self._config.is_win:
            return False
        try:
            import _bz2
        except ImportError:
            return True
        return False

    def install(self) -> None:
        """Install bz2"""
        if not self.needs_install():
            self._logger.info("_bz2 is already installed.")
            return
        try:
            bz_itm = self._bz2_config.get_config()
        except Exception as err:
            self._logger.error(f"Unable to get bz2 config: {err}")
            return
        progress: Progress | None = None
        if self.config.show_progress:
            self._logger.debug("Starting Progress Window")
            msg = self.resource_resolver.resolve_string("msg08")
            title = self.resource_resolver.resolve_string("title01") or self.config.lo_implementation_name
            progress = Progress(start_msg=f"{msg} _bz2", title=title)
            progress.start()
        else:
            self._logger.debug("Progress Window is disabled")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Do something with the temporary directory
                # print(f"Temporary directory created at {temp_dir}")
                path_bz2 = Path(temp_dir)

                url = str(bz_itm["url"])
                filename = path_bz2 / "embedded_py.zip"
                dl = Download()
                data, _, err = dl.url_open(url, verify=False)
                if err:
                    self._logger.error("Unable to download embedded python file")
                    return
                dl.save_binary(pth=filename, data=data)

                if filename.exists():
                    self._logger.info("embedded_py.zip file has been saved")
                else:
                    self._logger.error("Unable to copy embedded_py.zip file")
                    return

                if md5_str := str(bz_itm["md5"]):
                    if not self._verify_file(filename=filename, md5_str=md5_str):
                        self._logger.error("MD5 verification failed")
                        return
                    else:
                        self._logger.info("MD5 verification passed")
                unzip_path = path_bz2 / "embedded_py"
                if not unzip_path.exists():
                    unzip_path.mkdir()
                self._unzip(filename=filename, dst=unzip_path)

                bz_file = unzip_path / "_bz2.pyd"
                if not bz_file.exists():
                    self._logger.error("Unable to find _bz2.pyd file")
                    return
                self._copy_file(src=bz_file, dst=self._bz2_config.install_dir / "_bz2.pyd")

        finally:
            if progress:
                self._logger.debug("Ending Progress Window")
                progress.kill()

    def _copy_file(self, src: Path, dst: Path) -> None:
        """Copy file"""
        try:
            shutil.copy(src, dst)
            if dst.exists():
                self._logger.debug(f"File has been copied to {dst}")
            else:
                self._logger.error("File has not been copied")
                raise Exception("File has not been copied")
        except Exception as err:
            self._logger.error(f"Unable to copy file: {err}", exc_info=True)
            raise

    def _verify_file(self, filename: Path, md5_str: str) -> bool:
        result = hashlib.md5(open(filename, "rb").read()).hexdigest()
        return result == md5_str

    def _unzip(self, filename: Path, dst: str | Path) -> None:
        """Unzip the downloaded wheel file"""
        # sourcery skip: raise-specific-error
        if isinstance(dst, str):
            dst = Path(dst)
        try:
            file_util.unzip_file(filename, dst)
            if dst.exists():
                self._logger.debug(f"File has been unzipped to {dst}")
            else:
                self._logger.error("File has not been unzipped")
                raise Exception("File has not been unzipped")
        except Exception as err:
            self._logger.error(f"Unable to unzip file: {err}", exc_info=True)
            raise
