from __future__ import annotations
from typing import List, TYPE_CHECKING
from pathlib import Path
import ctypes
import _ctypes

# import pkg_resources
from ...oxt_logger import OxtLogger
from .install_pkg import InstallPkg
from .batch.batch_writer_ps1 import BatchWriterPs1
from ...input_output import file_util

if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override
else:

    def override(func: Any) -> Any:
        return func


class InstallPkgWin(InstallPkg):
    """Install pip packages for flatpak."""

    @override
    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    def _unlink_pyd(self, pth: Path, pkg_name: str) -> None:
        """Unlink the pyd file."""
        # https://stackoverflow.com/questions/46450368/removing-loaded-pyd-files

        def get_pyd_files(directory: Path) -> List[Path]:
            """Get all .pyd files from the directory recursively."""
            return list(directory.rglob("*.pyd"))

        pyd_files = get_pyd_files(pth)
        for pyd_file in pyd_files:
            try:
                dll = ctypes.CDLL(str(pyd_file))
                _ctypes.FreeLibrary(dll._handle)
                self.log.debug("Unlinked %s", pyd_file)
                try_mod_name = pyd_file.name.split(".")[0]
                # try something like matplotlib.ft2font
                self.unload_module(f"{pkg_name}.{try_mod_name}")
            except FileNotFoundError:
                self.log.debug("_unlink_pyd() File Not Found: %s", pyd_file)
            except OSError as e:
                self.log.exception("_unlink_pyd() Error unlinking %s: %s", pyd_file, e)

    @override
    def on_removing_dir(self, dir_path: Path, pkg_name: str) -> None:
        """Remove the directory."""
        self._unlink_pyd(dir_path, pkg_name)

    @override
    def on_extension_install(self) -> None:
        try:
            out_file = Path(
                file_util.get_user_profile_path(True),
                f"{self.config.cmd_clean_file_prefix}{self.config.lo_implementation_name}.ps1",
            )
            writer = BatchWriterPs1(self)
            with out_file.open("w", encoding="utf-8") as f:
                f.write(writer.get_contents())
            self.log.info("Cleanup script written to %s", out_file)
        except Exception as e:
            self.log.exception("Error writing cleanup script: %s", e)
