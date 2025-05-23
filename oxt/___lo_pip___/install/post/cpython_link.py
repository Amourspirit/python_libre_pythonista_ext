"""
On some systems such as Mac and AppImage (Linux) the python extension suffix does not match the
cpython suffix used by the embedded python interpreter.

This class creates symlinks for all .so files in site-packages that match the current python embedded suffix.

For example a file named ``indexers.cpython-38-x86_64-linux-gnu.so`` would be symlinked to ``indexers.cpython-3.8.so``.
This renaming allows the python interpreter to find the import.
"""

from __future__ import annotations
from typing import List, Union
from pathlib import Path
from importlib import machinery
import logging
from ...config import Config
from ...oxt_logger import OxtLogger


class CPythonLink:
    def __init__(self, overwrite: bool = False) -> None:
        """
        Constructor

        Args:
            overwrite (bool, optional): Override any existing sys links. Defaults to False.
        """
        self._overwrite = overwrite
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._current_suffix = self._get_current_suffix()  # .cpython-3.8.so
        self._logger.debug("CPythonLink.__init__")
        # self._suffix = self._get_current_suffix()
        self._config = Config()
        self._site_packages: Union[Path, None] = None
        self._file_suffix = ""
        if self._config.site_packages:
            self._site_packages = Path(self._config.site_packages)
            self._file_suffix = self._find_current_installed_suffix(self._site_packages)
        self._logger.debug("CPythonLink.__init__ done")

    def _get_current_suffix(self) -> str:
        """Gets suffix currently used by the embedded python interpreter such as ``cpython-3.8``"""
        # in windows suffixes are something like ['.cp39-win_amd64.pyd', '.pyd']
        for suffix in machinery.EXTENSION_SUFFIXES:
            if suffix.startswith(".cpython-") and suffix.endswith(".so"):
                # remove leading . and trailing .so
                return suffix[1:][:-3]
        return ""

    def get_needs_linking(self) -> bool:
        """Gets if the files need linking to fix .cpython issue."""
        # for normal installs the suffix will be something like cpython-312-x86_64-linux-gnu
        # for other embedded it will be something like .cpython-3.9
        # If the number of - occurrences are greater then 1 then linking should not be needed
        if self._config.is_win:
            self._logger.debug("get_needs_linking() Not needed on Windows")
            return False
        if not self._site_packages:
            self._logger.debug("get_needs_linking() No site-packages found")
            return False
        if not self._file_suffix:
            self._logger.debug("get_needs_linking() No current file suffix found")
            return False
        if not self._site_packages.exists():
            self._logger.debug(f"get_needs_linking() Site-packages does not exist {self._site_packages}")
            return False
        cp_old = self._file_suffix
        cp_new = self._current_suffix
        return cp_old != cp_new

        # suffix = self._get_current_suffix()
        # if not suffix:
        #     self._logger.warning("get_needs_linking() No suffix found for cpython")
        #     return False
        # count = suffix.count("-")
        # return count <= 1

    def _get_all_files(self, path: Path) -> List[Path]:
        return [p for p in path.glob(f"**/*{self._file_suffix}.so") if p.is_file()]

    def _create_symlink(self, src: Path, dst: Path) -> None:
        log = self._config.log_level <= logging.DEBUG
        if dst.is_symlink():
            if self._overwrite:
                if log:
                    self._logger.debug(f"Removing existing symlink {dst}")
                dst.unlink()
            else:
                if log:
                    self._logger.debug(f"Symlink already exists {dst}")
                return
        dst.symlink_to(src)
        if log:
            self._logger.debug(f"Created symlink {dst} -> {src}")

    def _find_current_installed_suffix(self, path: Path) -> str:
        """
        Finds the current suffix from the current installed python so files such as ``cpython-38-x86_64-linux-gnu``.

        Args:
            path (Path): Path to search in. Usually site-packages.

        Returns:
            str: suffix if found, otherwise empty string.
        """
        return next(
            (str(p).rsplit(".", 2)[1] for p in path.glob("**/*.cpython-*.so") if not p.is_symlink()),
            "",
        )

    def link(self) -> None:
        """
        Creates symlinks for all .so files in site-packages that match the current suffix.
        """
        self._logger.debug("link() starting")
        if not self._site_packages:
            self._logger.debug("link() No site-packages found")
            return
        if not self._file_suffix:
            self._logger.debug("link() No current file suffix found")
            return
        if not self._site_packages.exists():
            self._logger.debug(f"link() Site-packages does not exist {self._site_packages}")
            return
        self._logger.debug(f"link() Python current suffix: {self._current_suffix}")
        self._logger.debug(f"link() Found file suffix: {self._file_suffix}")
        files = self._get_all_files(self._site_packages)
        if not files:
            self._logger.debug(f"link() No files found in {self._site_packages}")
            return
        cp_old = self._file_suffix
        cp_new = self._current_suffix
        if cp_old == cp_new:
            self._logger.debug(f"link() Suffixes match, no need to link: {cp_old} == {cp_new}")
            return

        for file in files:
            ln_name = file.name.replace(cp_old, cp_new)
            src = file
            if not src.is_absolute():
                src = file.resolve()
            dst = src.parent / ln_name
            self._create_symlink(src, dst)
        self._logger.debug("link() done")

    def unlink(self) -> None:
        """
        Removes all symlinks that match the current suffix.
        """
        self._logger.debug("link remove_cpython_so_links()")
        if not self.get_needs_linking():
            return
        root_dir = self._site_packages
        if root_dir is None:
            return
        is_db = self._logger.is_debug
        for path in Path(root_dir).rglob(f"*{self._current_suffix}.so"):
            if path.is_symlink():
                try:
                    path.unlink()
                except Exception as e:
                    self._logger.error(f"link unlink() Error removing symlink: {path} {e}")
                if is_db:
                    self._logger.debug(f"link unlink() Removed symbolic link: {path}")
            else:
                if is_db:
                    self._logger.debug(f"link unlink() Skipped (not a symbolic link): {path}")
        else:
            if is_db:
                self._logger.debug(
                    f"link unlink() No symbolic links found in '{root_dir}' for '*{self._current_suffix}'"
                )

    # region Properties
    @property
    def cpy_name(self) -> str:
        """Gets/Sets CPython name, e.g. cpython-3.8"""
        return self._current_suffix

    @cpy_name.setter
    def cpy_name(self, value: str) -> None:
        self._current_suffix = value

    @property
    def overwrite(self) -> bool:
        """Gets/Sets if existing symlinks should be overwritten"""
        return self._overwrite

    @overwrite.setter
    def overwrite(self, value: bool) -> None:
        self._overwrite = value

    @property
    def current_suffix(self) -> str:
        """Current Suffix such as ``cpython-3.8``"""
        return self._current_suffix

    @property
    def file_suffix(self) -> str:
        """Current Suffix such as ``cpython-38-x86_64-linux-gnu``"""
        return self._file_suffix

    # endregion Properties
