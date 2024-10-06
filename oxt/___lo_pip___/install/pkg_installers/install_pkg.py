from __future__ import annotations
import os
import sys
import shutil
import subprocess
import glob
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


# import pkg_resources
import importlib.metadata
from importlib.metadata import PackageNotFoundError, version
from ...config import Config
from ...lo_util.resource_resolver import ResourceResolver
from ...lo_util.target_path import TargetPath
from ...oxt_logger import OxtLogger
from ...ver.rules.ver_rules import VerRules, VerProto
from ..download import Download
from ..progress import Progress


# https://docs.python.org/3.8/library/importlib.metadata.html#module-importlib.metadata
# https://stackoverflow.com/questions/44210656/how-to-check-if-a-module-is-installed-in-python-and-if-not-install-it-within-t

# https://stackoverflow.com/search?q=%5Bpython%5D+run+subprocess+without+popup+terminal
# silent subprocess
if os.name == "nt":
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None


class InstallPkg:
    """Install pip packages."""

    def __init__(self, ctx: Any, flag_upgrade: bool = True, **kwargs: Any) -> None:
        """Constructor

        Args:
            ctx (Any): The context.
            flag_upgrade (bool, optional): Specifies if the upgrade flag should be used. Defaults to True.

        Keyword Args:
            show_progress (bool, optional): Specifies if the progress window should be shown. Defaults to ``Config.show_progress``.

        Returns:
            None:
        """
        self.ctx = ctx
        self._config = Config()
        self._path_python = Path(self._config.python_path)
        self._ver_rules = VerRules()
        self._logger = self._get_logger()
        self._flag_upgrade = flag_upgrade
        self._show_progress = bool(kwargs.get("show_progress", self._config.show_progress))
        self._resource_resolver = ResourceResolver(ctx=self.ctx)
        self._target_path = TargetPath()
        self._no_pip_remove = self._config.no_pip_remove  # {"pip", "setuptools", "wheel"}

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    def get_package_version(self, package_name: str) -> str:
        """
        Get the version of a package.

        Args:
            package_name (str): The name of the package such as ``verr``

        Returns:
            str: The version of the package or an empty string if the package is not installed.
        """
        try:
            return version(package_name)
        except PackageNotFoundError:
            return ""

    def _cmd_pip(self, *args: str) -> List[str]:
        cmd: List[str] = [str(self._path_python), "-m", "pip", *args]
        if self._config.log_pip_installs and self._config.log_file:
            log_file = self._config.log_file

            if " " in log_file:
                log_file = f'"{log_file}"'
            cmd.append(f"--log={log_file}")
        return cmd

    def _install_pkg(self, pkg: str, ver: str, force: bool) -> bool:
        """
        Install a package.

        Args:
            pkg (str): The name of the package to install.
            ver (str): The version of the package to install.
            force (bool): Force install even if package is already installed.

        Returns:
            bool: True if successful, False otherwise.
        """
        auto_target = False
        if self.config.auto_install_in_site_packages:
            if self.config.site_packages:
                auto_target = True
            else:
                self._logger.debug(
                    "auto_install_in_site_packages is set to True; However, No site-packages directory set in configuration. site_packages value should be set in lo_pip.config.py"
                )
                self._logger.debug(
                    "Ignoring auto_install_in_site_packages and continuing to install in user directory via pip --user"
                )
        cmd = ["install"]
        if force:
            cmd.append("--force-reinstall")
        elif self.flag_upgrade:
            cmd.append("--upgrade")

        if not auto_target and self.config.is_win and len(self.config.isolate_windows) > 0:
            auto_target = True

        if auto_target:
            cmd.append(f"--target={self._target_path.get_package_target(pkg)}")
        elif self.config.is_user_installed:
            cmd.append("--user")

        pkg_cmd = f"{pkg}{ver}" if ver else pkg
        cmd = self._cmd_pip(*[*cmd, pkg_cmd])
        self._logger.debug(f"Running command {cmd}")
        self._logger.info(f"Installing package {pkg}")
        if self._flag_upgrade:
            msg = f"Pip Install - Upgrading success for: {pkg_cmd}"
            err_msg = f"Pip Install - Upgrading failed for: {pkg_cmd}"
        else:
            msg = f"Pip Install success for: {pkg_cmd}"
            err_msg = f"Pip Install failed for: {pkg_cmd}"

        site_packages_dir = self._get_site_packages_dir(pkg)
        if pkg in self.no_pip_remove:  # ignore pip
            is_ignore = True
            before_dirs = []
            before_files = []
        else:
            is_ignore = False
            before_dirs = self._get_directory_names(site_packages_dir)
            before_files = self._get_file_names(site_packages_dir)

        progress: Progress | None = None
        if self._config.show_progress and self.show_progress:
            # display a terminal window to show progress
            self._logger.debug("Starting Progress Window")
            msg = self.resource_resolver.resolve_string("msg08")
            title = self.resource_resolver.resolve_string("title01") or self.config.lo_implementation_name
            progress = Progress(start_msg=f"{msg}: {pkg}", title=title)
            progress.start()
        else:
            self._logger.debug("Progress Window is disabled")

        if STARTUP_INFO:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
                text=True,
                env=self._get_env(),
                startupinfo=STARTUP_INFO,
            )
        else:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
                text=True,
                env=self._get_env(),
            )

        result = False
        if process.returncode == 0:
            if not is_ignore:
                self._delete_json_file(site_packages_dir, pkg)
                after_dirs = self._get_directory_names(site_packages_dir)
                after_files = self._get_file_names(site_packages_dir)
                self._save_changed(
                    pkg=pkg,
                    pth=site_packages_dir,
                    before_files=before_files,
                    after_files=after_files,
                    before_dirs=before_dirs,
                    after_dirs=after_dirs,
                )
            self._logger.info(msg)
            result = True
        else:
            self._logger.error(err_msg)
            try:
                self._logger.error(process.stderr)
            except Exception as err:
                self._logger.error(f"Error decoding stderr: {err}")

        if progress:
            self._logger.debug("Ending Progress Window")
            progress.kill()

        return result

    def uninstall_pkg(self, pkg: str, target: str = "") -> bool:
        """
        Uninstall a package by manually removing its directory and dist-info folder from the target location.

        Args:
            pkg (str): The name of the package to uninstall.
            target (str, optional): The target directory where the package is installed. Defaults to the extension target path.

        Returns:
            bool: True if the package was uninstalled successfully, False otherwise.
        """
        if pkg in self.no_pip_remove:
            self.log.debug(f"{pkg} is in the no install list. Not Uninstalling and continuing.")
            return True

        def find_matching_files(directory: str, pattern: str) -> list:
            search_pattern = os.path.join(directory, pattern)
            return glob.glob(search_pattern)

        if not target:
            target = self._target_path.get_package_target(pkg)
        if self.log.is_debug:
            self.log.debug(f"uninstall_package() pkg: {pkg}, target: {target}")
            if os.path.exists(target):
                self.log.debug(f"uninstall_package() target: {target}")
            else:
                self.log.debug(f"uninstall_package() target {target} does not exist.")

        package_dir = os.path.join(target, pkg)
        self.log.debug(f"uninstall_package() package_dir: {package_dir}")
        dist_info_dir = self.find_dist_info(pkg, target)
        self.log.debug(f"uninstall_package() dist_info_dir: {dist_info_dir}")

        success = True
        step = 1

        if dist_info_dir:
            if os.path.exists(dist_info_dir):
                try:
                    shutil.rmtree(dist_info_dir)
                    self.log.info(f"uninstall_package() Successfully removed {dist_info_dir}. Step {step}")
                except Exception as e:
                    self.log.exception(f"uninstall_package() Failed to remove {dist_info_dir}: {e}. Step {step}")
                    success = False
            else:
                self.log.debug(f"uninstall_package() {dist_info_dir} not found. Step {step}")
        else:
            self.log.debug(f"uninstall_package() no dist-info found for {pkg}. Step {step}")

        step = 2
        if not success:
            self.log.error(f"uninstall_package() Incomplete removal for {pkg} in step {step}")
            return False

        if os.path.exists(package_dir):
            try:
                shutil.rmtree(package_dir)
                self.log.info(f"uninstall_package() Successfully removed {pkg} from {target}. Step {step}")
            except Exception as e:
                self.log.exception(f"uninstall_package() Failed to remove {pkg} from {target}: {e}. Step {step}")
                success = False
        else:
            self.log.debug(f"uninstall_package() {pkg} not found in {target}. Step {step}")

        # just in case there are multiple dist-info folders from previous bad uninstalls,
        # we will remove all of them.
        step = 3
        if not success:
            self.log.error(f"uninstall_package() Incomplete removal for {pkg} in step {step}")
            return False

        patterns = (f"{pkg}-*.dist-info", f"{pkg.replace('-', '_')}*.dist-info")
        for dist_info_pattern in patterns:
            dist_info_dirs = find_matching_files(target, dist_info_pattern)
            for dist_info_dir in dist_info_dirs:
                if os.path.exists(dist_info_dir):
                    try:
                        shutil.rmtree(dist_info_dir)
                        self.log.info(f"uninstall_package() Successfully removed {dist_info_dir}. Step {step}")
                    except Exception as e:
                        self.log.exception(f"uninstall_package() Failed to remove {dist_info_dir}: {e}. Step {step}")
                        success = False
                else:
                    self.log.debug(f"uninstall_package() {dist_info_dir} not found. Step {step}")
            if self.log.is_debug:
                self.log.debug(f"uninstall_package() dist_info_dirs: {dist_info_dirs}. Step {step}")
                if not dist_info_dirs:
                    self.log.debug(
                        f"uninstall_package() dist_info_pattern: {dist_info_pattern} found no more dist-info folders. Step {step}"
                    )

        step = 4
        if not success:
            self.log.error(f"uninstall_package() Incomplete removal for {pkg} in step {step}")
            return False

        if success:
            if pkg_dir := self.get_package_installation_dir(pkg):
                try:
                    shutil.rmtree(pkg_dir)
                    self.log.info(f"uninstall_package() Successfully removed {pkg_dir}. Step {step}")
                except Exception as e:
                    self.log.error(
                        f"uninstall_package() Failed to remove {pkg_dir}: {e}. Not critical so will continue. Step {step}"
                    )
                    # this is not critical so we will continue

        step = 5
        if not success:
            self.log.error(f"uninstall_package() Incomplete removal for {pkg} in step {step}")
            return False

        return success

    def _get_env(self) -> Dict[str, str]:
        """
        Gets Environment used for subprocess.
        """
        my_env = os.environ.copy()
        py_path = ""
        p_sep = ";" if os.name == "nt" else ":"
        for d in sys.path:
            py_path = py_path + d + p_sep
        my_env["PYTHONPATH"] = py_path
        return my_env

    def install(self, req: Dict[str, str] | None = None, force: bool = False) -> bool:
        """
        Install all the packages in the configuration if they are not already installed and meet requirements.

        Args:
            req (Dict[str, str] | None, optional): The requirements to install.
                If omitted then requirements from config are used. Defaults to None.
            force (bool, optional): Force install even if package is already installed. Defaults to False.

        Returns:
            bool: True if all packages are installed successful, False otherwise.
        """
        self._logger.info("Installing packages…")

        req = req or self._config.requirements

        if not req:
            self._logger.warning("No packages to install.")
            return False

        result = True
        for name, ver in req.items():
            valid, rules = self._is_valid_version(name, ver, force)
            if force:
                valid = 0
            if valid == 1:
                continue

            if not self.is_internet:
                self._logger.error("No internet connection!")
                break

            ver_lst: List[str] = [rule.get_versions_str() for rule in rules]
            if self.config.uninstall_on_update:
                pkg_ver = self.get_package_version(name)
                if pkg_ver:
                    self.log.debug(f"Package {name} {pkg_ver} already installed. Attempting to uninstall.")
                    try:
                        if not self.uninstall_pkg(name):
                            return False
                    except PermissionError as e:
                        if self.config.install_on_no_uninstall_permission:
                            self._logger.error(f"Unable to uninstall {name}. {e}")
                            self._logger.info(
                                "Permission error is usually because the package is installed as a system package that LibreOffice does not have permission to uninstall."
                            )
                            self._logger.info(
                                f"Continuing to install {name} {ver} even though it is already installed. Probably because it is installed as a system package."
                            )
                        else:
                            self._logger.error(
                                f"Unable to uninstall {name}. {e}\nThis is usually because the package is installed as a system package that LibreOffice does not have permission to uninstall."
                            )
                            return False
            result = result and self._install_pkg(name, ",".join(ver_lst), force)
        self._logger.info("Installing packages Done!")
        return result

    def install_file(self, pth: str | Path, force: bool = False) -> bool:
        """
        Install all the packages in the configuration if they are not already installed and meet requirements.

        Args:
            req (Dict[str, str] | None, optional): The requirements to install.
                If omitted then requirements from config are used. Defaults to None.
            force (bool, optional): Force install even if package is already installed. Defaults to False.

        Returns:
            None:
        """
        self._logger.info("Installing packages…")
        if isinstance(pth, str):
            pth = Path(pth)
        if not pth.exists():
            self._logger.error(f"Cannot install File. Does not exist: {pth}")
            return False

        result = self._install_pkg(pkg=str(pth), ver="", force=force)
        self._logger.info(f"Install file package {pth.name} Done!")
        return result

    def _is_valid_version(self, name: str, ver: str, force: bool) -> Tuple[int, List[VerProto]]:
        """
        Check if the version of the package is valid.

        Args:
            name (str): The name of the package such as ``verr``. If empty string the version is converted to ``>=0.0.0``
            ver (str): The version of the package such as ``>=1.0.0``
            force (bool, optional): Force the package to install even if it is already installed. Defaults to False.

        Returns:
            Tuple[int, List[VerProto]]: int is 0 if valid, 1 if not valid, -1 if not installed
        """
        if not ver:
            # set default version to >=0.0.0
            ver = "==*"
        pkg_ver = self.get_package_version(name)
        rules = self._ver_rules.get_matched_rules(ver)
        if not pkg_ver:
            self._logger.debug(f"Package {name} not installed. Setting Install flags.")
            return 0, rules

        self._logger.debug(f"Found Package {name} {pkg_ver} already installed ...")
        if not rules:
            if pkg_ver:
                self._logger.info(f"Package {name} {pkg_ver} already installed, no rules")
            else:
                self._logger.error(f"Unable to Install. Unable to find rules for {name} {ver}")
            return 1, rules

        rules_pass = self._ver_rules.get_installed_is_valid_by_rules(rules=rules, check_version=pkg_ver)
        if not rules_pass:
            self._logger.info(
                f"Package {name} {pkg_ver} already installed. It does not meet requirements specified by: {ver}, but will be upgraded."
            )
            return 0, rules
        if not force:
            self._logger.info(
                f"Package {name} {pkg_ver} already installed; However, it does not need to be installed to meet constraints: {ver}. It will be skipped."
            )
        return 1, rules

    def find_dist_info(self, pkg: str, target: str) -> str:
        """
        Find the dist-info folder for a package in the target directory.

        Args:
            package_name (str): The name of the package.
            target (str): The target directory where the package is installed.

        Returns:
            str: The path to the dist-info folder, or an empty string if not found.
        """
        # do not use pkg_resources as it is deprecated and does not work on windows.

        def convert_to_local(pth: Path) -> Path:
            return Path(target, pth.name)

        try:
            dist = importlib.metadata.distribution(pkg)
            location = dist.locate_file("")
            dist_info_folder = f"{pkg.replace('-', '_')}-{dist.version}.dist-info"
            dist_info_path = Path(str(location), dist_info_folder)
            dist_info_path = convert_to_local(dist_info_path)
            if dist_info_path.exists():
                return str(dist_info_path)
            return ""
        except importlib.metadata.PackageNotFoundError:
            return ""

    def get_package_installation_dir(self, pkg: str) -> str:
        """
        Get the installation directory of a package.

        Args:
            pkg (str): The name of the package.

        Returns:
            str: The path to the installation directory, or an empty string if not found.
        """
        result = Path(self._target_path.get_package_target(pkg), pkg.replace("-", "_"))
        if result.exists():
            self.log.debug(f"get_package_installation_dir() result: {result}")
            return str(result)
        else:
            self.log.debug(f"get_package_installation_dir() result: {result} not found")
        return ""

    # region Json directory methods
    def _get_site_packages_dir(self, pkg: str) -> str:
        """Get the site-packages directory."""
        return self._target_path.get_package_target(pkg)

    def _get_file_names(self, path: str) -> List[str]:
        # only get the file names in the specified path
        return [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

    def _get_directory_names(self, path: str) -> List[str]:
        """Get the directory names in the specified path."""
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def _save_changed(
        self,
        pkg: str,
        pth: str,
        before_files: List[str],
        after_files: List[str],
        before_dirs: List[str],
        after_dirs: List[str],
    ) -> None:
        """Save the new directory names to a JSON file."""

        def _create_json() -> str:
            """Create a JSON file with the file names."""
            new_dirs = list(set(after_dirs) - set(before_dirs))
            new_files = list(set(after_files) - set(before_files))
            data = {
                "id": f"{self._config.oxt_name}_pip_pkg",
                "package": pkg,
                "version": self._config.extension_version,
                "data": {"new_dirs": new_dirs, "new_files": new_files},
            }
            return json.dumps(data, indent=4)

        try:
            json_str = _create_json()
            json_path = os.path.join(pth, f"{self._config.lo_implementation_name}_{pkg}.json")
            with open(json_path, "w") as f:
                f.write(json_str)
            self._logger.info(f"New directories and files saved to {json_path}")
        except Exception as e:
            self._logger.exception(f"Error saving new directories and files: {e}")

    def _delete_json_file(self, path: str, pkg: str) -> None:
        """Delete the JSON file if it exists."""
        json_path = os.path.join(path, f"{self._config.lo_implementation_name}_{pkg}.json")
        if os.path.exists(json_path):
            os.remove(json_path)
            self._logger.info(f"Deleted {json_path}")

    # get the json data from the file if it exists
    def _get_json_data(self, path: str, pkg: str) -> Dict[str, Any]:
        """Get the JSON data from the file if it exists."""
        json_path = os.path.join(path, f"{self._config.lo_implementation_name}_{pkg}.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                return json.load(f)
        return {}

    def _remove_json_data(self, path: str, pkg: str) -> None:
        """Remove the JSON data if it exists."""
        json_path = os.path.join(path, f"{self._config.lo_implementation_name}_{pkg}.json")
        if os.path.exists(json_path):
            os.remove(json_path)
            self._logger.info(f"Deleted {json_path}")

    # check and see if there are any directories and files that need to be removed. Us the Json file to get the data
    def _remove_changed(self, pkg: str, pth: str) -> None:
        """Remove the new directories and files."""
        data_dict = self._get_json_data(pth, pkg)
        data: Dict[str, str] = data_dict.get("data", {})
        new_dirs = data.get("new_dirs", [])
        new_files = data.get("new_files", [])
        for d in new_dirs:
            dir_path = os.path.join(pth, d)
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    self._logger.info(f"_remove_changed() Removed directory: {d}")
                else:
                    self._logger.debug(f"_remove_changed() Directory {d} does not exist.")
            except Exception as e:
                self._logger.error(f"_remove_changed() Error removing directory {d}: {e}")
        for f in new_files:
            file_path = os.path.join(pth, f)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self._logger.info(f"_remove_changed() Removed file: {f}")
                else:
                    self._logger.debug(f"_remove_changed() File {f} does not exist.")
            except Exception as e:
                self._logger.error(f"_remove_changed() Error removing file {f}: {e}")
        self._remove_json_data(pth, pkg)
        self._logger.info("Removed new directories and files.")

    # endregion Json directory methods

    @property
    def config(self) -> Config:
        return self._config

    @property
    def is_internet(self) -> bool:
        """Gets if there is an internet connection."""
        try:
            return self._is_internet
        except AttributeError:
            self._is_internet = Download().is_internet
            return self._is_internet

    @property
    def python_path(self) -> Path:
        return self._path_python

    @property
    def flag_upgrade(self) -> bool:
        """Gets if the packages should be installed with  --upgrade flag."""
        return self._flag_upgrade

    @property
    def show_progress(self) -> bool:
        """
        Gets/Sets if the progress window should be shown.

        ``Config.show_progress`` is used by default and ``Config.show_progress`` must be ``True`` for this to be used.
        """
        return self._show_progress

    @show_progress.setter
    def show_progress(self, value: bool) -> None:
        """Sets if the progress window should be shown."""
        self._show_progress = value

    @property
    def resource_resolver(self) -> ResourceResolver:
        """Gets the resource resolver."""
        return self._resource_resolver

    @property
    def log(self) -> OxtLogger:
        """Gets the logger."""
        return self._logger

    @property
    def no_pip_remove(self) -> set:
        return self._no_pip_remove
