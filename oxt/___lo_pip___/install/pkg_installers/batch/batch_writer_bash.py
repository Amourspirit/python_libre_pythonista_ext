"""
This module writes the batch file for windows cleanup.
"""

from __future__ import annotations
from typing import Dict, Iterable, Set, Tuple
from pathlib import Path
from .batch_writer import BatchWriter
from ..pkg_install_data import PkgInstallData
from ....lo_util.str_list import StrList


class BatchWriterBash(BatchWriter):
    def __init__(self) -> None:
        super().__init__()
        self._line_sep = "\n"  # os.linesep
        self._script_file: None | Path = None

    def _write_remove_dirs_fn(self, sw: StrList) -> None:
        """
        Write the function to remove files and directories.

        Args:
            sw (StringWriter): The StringWriter to write to.
        """
        sw.append("remove_dirs() {")
        with sw.indented():
            sw.append("local IFS=$'\\n' # Set Internal Field Separator to newline")
            sw.append("local -a folders=($@)")
            sw.append('for folder in "${folders[@]}"; do')
            with sw.indented():
                sw.append('if [[ -d "$folder" ]]; then')
                with sw.indented():
                    sw.append('rm -rf "$folder"')
                    sw.append('echo "Deleted folder: $folder"')
                    sw.append('rm -rf "$folder"')
                sw.append("else")
                with sw.indented():
                    sw.append('echo "Folder not found: $folder"')
                sw.append("fi")
            sw.append("done")
        sw.append("}")
        sw.append()

    def _write_remove_files_fn(self, sw: StrList) -> None:
        """
        Write the function to remove files and directories.

        Args:
            sw (StringWriter): The StringWriter to write to.
        """
        sw.append("remove_files() {")
        with sw.indented():
            sw.append("local IFS=$'\\n' # Set Internal Field Separator to newline")
            sw.append("local -a files=($@)")
            sw.append('for file in "${files[@]}"; do')
            with sw.indented():
                sw.append('if [[ -f "$file" ]]; then')
                with sw.indented():
                    sw.append('rm -f "$file"')
                    sw.append('echo "Deleted file: $file"')
                sw.append("else")
                with sw.indented():
                    sw.append('echo "File not found: $file"')
                sw.append("fi")
            sw.append("done")
        sw.append("}")
        sw.append()

    def _write_remove_folders(self, target_path: str, sw: StrList, dirs: Iterable[str]) -> None:
        """
        Write the remove folders call.

        Args:
            sw (StringWriter): The StringWriter to write to.
            dirs (Iterable[str]): The directories to remove.
        """
        if not dirs:
            return

        sw.append("dirs_to_remove=$(cat << EOF")
        for d in dirs:
            p = Path(target_path, d)
            sw.append(str(p))
        sw.append("EOF")
        sw.append(")")
        sw.append()
        sw.append('remove_dirs "${dirs_to_remove[@]}"')
        sw.append()

    def _write_remove_files(self, target_path: str, sw: StrList, files: Iterable[str]) -> None:
        """
        Write the remove files call.

        Args:
            sw (StringWriter): The StringWriter to write to.
            files (Iterable[str]): The files to remove.
        """
        if not files:
            return

        sw.append("files_to_remove=$(cat << EOF")
        for f in files:
            p = Path(target_path, f)
            sw.append(str(p))
        sw.append("EOF")
        sw.append(")")
        sw.append()
        sw.append('remove_files "${files_to_remove[@]}"')
        sw.append()

    def _write_output_for_pkg(self, pkg: PkgInstallData, sw: StrList) -> None:
        """
        Get the text for a file.

        Args:
            pkg (PkgInstallData): The package data.
            sw (StringWriter): The StringWriter to write to.

        Returns:
            None: None
        """
        try:
            if not pkg.package:
                raise ValueError("Package name not found")
            target_path = Path(self.target_path.get_package_target(pkg.package))

            dirs = pkg.new_dirs
            self._write_remove_folders(str(target_path), sw, dirs)

            files = pkg.new_files
            self._write_remove_files(str(target_path), sw, files)

            for pip_dir in self.config.pip_shared_dirs:
                key = f"new_{pip_dir}_files"
                files = pkg.get_files(key)
                self._write_remove_files(str(target_path / pip_dir), sw, files)

        except Exception as e:
            self.log.exception("Error writing output for %s: %s", pkg.package or "unknown", e)

    def _get_file_names(self, sw: StrList) -> Set[str]:
        """
        Get the file names.

        Returns:
            set[str]: The file names.
        """

        f_names: Set[str] = set()
        results: Dict[Tuple[str, str], set] = {}
        pkgs = self.packages.get_all_packages(all_pkg=True)
        remove_json_files: Dict[str, Set[str]] = {}
        for tp in self.target_path.get_targets():
            if not tp in remove_json_files:
                remove_json_files[tp] = set()

            for pkg in pkgs:
                json_name = f"{self.config.lo_implementation_name}_{pkg.name}.json"
                if not tp in results:
                    results[tp, json_name] = set()
                file_path = Path(tp, json_name)
                if file_path.exists():
                    str_p = str(file_path)
                    results[tp, json_name].add(str(file_path))
                    remove_json_files[tp].add(str_p)

        for _, files in results.items():
            f_names.update(files)

        for key, value in remove_json_files.items():
            self._write_remove_files(key, sw, value)

        return f_names

    def get_contents(self) -> str:
        """
        Get the contents of the batch file.

        Returns:
            str: Contents of the batch file
        """
        sw = StrList(sep=self._line_sep)
        self._write_remove_dirs_fn(sw)
        self._write_remove_files_fn(sw)
        data_files = self._get_file_names(sw)
        for file in data_files:
            pkg = PkgInstallData.from_file(Path(file))
            self._write_output_for_pkg(pkg, sw)

        return sw.to_string()

    def write_file(self) -> None:
        """
        Write the file.
        """
        try:
            with self.script_file.open("w", encoding="utf-8") as f:
                f.write(self.get_contents())
        except Exception as e:
            self.log.exception("Error writing file: %s", e)

    @property
    def script_file(self) -> Path:
        if not self._script_file:
            from ....input_output import file_util

            self._script_file = Path(
                file_util.get_user_profile_path(True),
                f"{self.config.cmd_clean_file_prefix}{self.config.lo_implementation_name}.sh",
            )
        return self._script_file
