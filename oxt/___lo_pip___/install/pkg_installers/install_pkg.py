from __future__ import annotations
import os
import sys
import shutil
import subprocess
import glob
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set


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
from ..py_packages.packages import Packages
from ...settings.install_settings import InstallSettings


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

    def __init__(self, ctx: Any, flag_upgrade: bool = True, **kwargs: Any) -> None:  # noqa: ANN401
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
        self._no_pip_remove = self._config.no_pip_remove.copy()  # {"pip", "setuptools", "wheel"}
        install_settings = InstallSettings()
        self._no_pip_install = install_settings.no_install_packages.copy()

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
        if pkg in self.no_pip_install:
            self._logger.debug("_install_pkg() %s is in the no install list. Not Installing and continuing.", pkg)
            return True

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
            before_bin_files = []
            before_lib_files = []
            before_inc_files = []
        else:
            is_ignore = False
            before_dirs = self._get_directory_names(site_packages_dir)
            before_files = self._get_file_names(site_packages_dir)
            before_bin_files = self._get_file_names(Path(site_packages_dir, "bin"))
            before_lib_files = self._get_file_names(Path(site_packages_dir, "lib"))
            before_inc_files = self._get_file_names(Path(site_packages_dir, "include"))

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

        result = False
        if process.returncode == 0:
            if not is_ignore:
                self._delete_json_file(site_packages_dir, pkg)
                after_dirs = self._get_directory_names(site_packages_dir)
                after_files = self._get_file_names(site_packages_dir)
                after_bin_files = self._get_file_names(Path(site_packages_dir, "bin"))
                after_lib_files = self._get_file_names(Path(site_packages_dir, "lib"))
                after_inc_files = self._get_file_names(Path(site_packages_dir, "include"))
                changes = {
                    "before_files": before_files,
                    "before_dirs": before_dirs,
                    "before_bin_files": before_bin_files,
                    "before_lib_files": before_lib_files,
                    "before_inc_files": before_inc_files,
                    "after_files": after_files,
                    "after_dirs": after_dirs,
                    "after_bin_files": after_bin_files,
                    "after_lib_files": after_lib_files,
                    "after_inc_files": after_inc_files,
                }
                self._save_changed(pkg=pkg, pth=site_packages_dir, changes=changes)
            self._logger.info(msg)
            result = True
        else:
            self._logger.error(err_msg)
            try:
                self._logger.error(process.stderr)
            except Exception as err:
                self._logger.error("Error decoding stderr: %s", err)

        if progress:
            self._logger.debug("Ending Progress Window")
            progress.kill()

        return result

    def uninstall_pkg(self, pkg: str, target: str = "", remove_tracking_file: bool = False) -> bool:
        """
        Uninstall a package by manually removing its directory and dist-info folder from the target location.

        Args:
            pkg (str): The name of the package to uninstall.
            target (str, optional): The target directory where the package is installed. Defaults to the extension target path.
            remove_tracking_file (bool, optional): Remove the tracking file for the package. Defaults to False.

        Returns:
            bool: True if the package was uninstalled successfully, False otherwise.
        """
        if pkg in self.no_pip_remove:
            self.log.debug("%s is in the no install list. Not Uninstalling and continuing.", pkg)
            return True

        def find_matching_files(directory: str, pattern: str) -> list:
            search_pattern = os.path.join(directory, pattern)
            return glob.glob(search_pattern)

        step = 1
        self.log.debug(
            "Attempting to uninstalling package via json package info for %s: Step %i",
            pkg,
            step,
        )
        site_packages_dir = self._get_site_packages_dir(pkg)
        self._remove_changed(site_packages_dir, pkg)

        if not target:
            target = self._target_path.get_package_target(pkg)
        if self.log.is_debug:
            self.log.debug("uninstall_package() pkg: %s, target: %s", pkg, target)
            if os.path.exists(target):
                self.log.debug("uninstall_package() target: %s", target)
            else:
                self.log.debug("uninstall_package() target %s does not exist.", target)

        package_dir = os.path.join(target, pkg)
        self.log.debug("uninstall_package() package_dir: %s", package_dir)
        dist_info_dir = self.find_dist_info(pkg, target)
        self.log.debug("uninstall_package() dist_info_dir: %s", dist_info_dir)

        success = True
        step = 2

        if dist_info_dir:
            if os.path.exists(dist_info_dir):
                try:
                    shutil.rmtree(dist_info_dir)
                    self.log.info(
                        "uninstall_package() Successfully removed %s. Step %i",
                        dist_info_dir,
                        step,
                    )
                except Exception as e:
                    self.log.exception(f"uninstall_package() Failed to remove {dist_info_dir}: {e}. Step {step}")
                    success = False
            else:
                self.log.debug("uninstall_package() %s not found. Step %i", dist_info_dir, step)
        else:
            self.log.debug("uninstall_package() no dist-info found for %s. Step %i", pkg, step)

        step = 3
        if not success:
            self.log.error("uninstall_package() Incomplete removal for %s in step %i", pkg, step)
            return False

        if os.path.exists(package_dir):
            try:
                shutil.rmtree(package_dir)
                self.log.info(
                    "uninstall_package() Successfully removed %s from %s. Step %i",
                    pkg,
                    target,
                    step,
                )
            except Exception as e:
                self.log.exception(
                    "uninstall_package() Failed to remove %s from %s: %s. Step %i",
                    pkg,
                    target,
                    e,
                    step,
                )
                success = False
        else:
            self.log.debug("uninstall_package() %s not found in %s. Step %i", pkg, target, step)

        # just in case there are multiple dist-info folders from previous bad uninstalls,
        # we will remove all of them.
        step = 4
        if not success:
            self.log.error("uninstall_package() Incomplete removal for %s in step %i", pkg, step)
            return False

        patterns = (f"{pkg}-*.dist-info", f"{pkg.replace('-', '_')}*.dist-info")
        for dist_info_pattern in patterns:
            dist_info_dirs = find_matching_files(target, dist_info_pattern)
            for dist_info_dir in dist_info_dirs:
                if os.path.exists(dist_info_dir):
                    try:
                        shutil.rmtree(dist_info_dir)
                        self.log.info(
                            "uninstall_package() Successfully removed %s. Step %i",
                            dist_info_dir,
                            step,
                        )
                    except Exception as e:
                        self.log.exception(
                            "uninstall_package() Failed to remove %s: %s. Step %i",
                            dist_info_dir,
                            e,
                            step,
                        )
                        success = False
                else:
                    self.log.debug("uninstall_package() %s not found. Step %i", dist_info_dir, step)
            if self.log.is_debug:
                self.log.debug(
                    "uninstall_package() dist_info_dirs: %s. Step %i",
                    dist_info_dirs,
                    step,
                )
                if not dist_info_dirs:
                    self.log.debug(
                        "uninstall_package() dist_info_pattern: %s found no more dist-info folders. Step %i",
                        dist_info_dir,
                        step,
                    )

        step = 5
        if not success:
            self.log.error("uninstall_package() Incomplete removal for %s in step %i", pkg, step)
            return False

        if success and (pkg_dir := self.get_package_installation_dir(pkg)):
            try:
                shutil.rmtree(pkg_dir)
                self.log.info(
                    "uninstall_package() Successfully removed %s. Step %i",
                    pkg_dir,
                    step,
                )
            except Exception as e:
                self.log.error(
                    "uninstall_package() Failed to remove %s: %s. Not critical so will continue. Step %i",
                    pkg_dir,
                    e,
                    step,
                )
                # this is not critical so we will continue
        step = 6
        if remove_tracking_file:
            site_packages_dir = self._get_site_packages_dir(pkg)
            self._delete_json_file(site_packages_dir, pkg)
            self.log.info("uninstall_package() Removed tracking file for %s", pkg)
            self.log.debug("uninstall_package() Removed tracking file for %s. Completed Step %i", pkg, step)
        else:
            self.log.debug("uninstall_package() Not removing tracking file for %s: skipping step %i", pkg, step)

        step = 7
        if not success:
            self.log.error("uninstall_package() Incomplete removal for %s in step %i", pkg, step)
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

        if req is None:
            packages = Packages()

            req = self._config.requirements.copy()
            req.update(packages.to_dict())
        else:
            self._logger.debug("Using requirements from parameter.")

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
                    self.log.debug(
                        "Package %s %s already installed. Attempting to uninstall.",
                        name,
                        pkg_ver,
                    )
                    try:
                        if not self.uninstall_pkg(name):
                            return False
                    except PermissionError as e:
                        if self.config.install_on_no_uninstall_permission:
                            self._logger.error("Unable to uninstall %s. %s", name, e)
                            self._logger.info(
                                "Permission error is usually because the package is installed as a system package that LibreOffice does not have permission to uninstall."
                            )
                            self._logger.info(
                                "Continuing to install %s %s even though it is already installed. Probably because it is installed as a system package.",
                                name,
                                ver,
                            )
                        else:
                            self._logger.error(
                                "Unable to uninstall %s. %s\nThis is usually because the package is installed as a system package that LibreOffice does not have permission to uninstall.",
                                name,
                                e,
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
            self._logger.debug("Package %s not installed. Setting Install flags.", name)
            return 0, rules

        self._logger.debug("Found Package %s %s already installed ...", name, pkg_ver)
        if not rules:
            if pkg_ver:
                self._logger.info("Package %s %s already installed, no rules", name, pkg_ver)
            else:
                self._logger.error("Unable to Install. Unable to find rules for %s %s", name, ver)
            return 1, rules

        rules_pass = self._ver_rules.get_installed_is_valid_by_rules(rules=rules, check_version=pkg_ver)
        if not rules_pass:
            self._logger.info(
                "Package %s %s already installed. It does not meet requirements specified by: %s, but will be upgraded.",
                name,
                pkg_ver,
                ver,
            )
            return 0, rules
        if not force:
            self._logger.info(
                "Package %s %s already installed; However, it does not need to be installed to meet constraints: %s. It will be skipped.",
                name,
                pkg_ver,
                ver,
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
            self.log.debug("get_package_installation_dir() result: %s", result)
            return str(result)
        else:
            self.log.debug("get_package_installation_dir() result: %s not found", result)
        return ""

    # region Json directory methods
    def _get_site_packages_dir(self, pkg: str) -> str:
        """Get the site-packages directory."""
        return self._target_path.get_package_target(pkg)

    def _get_file_names(self, path: str | Path) -> List[str]:
        # only get the file names in the specified path

        pth = Path(path) if isinstance(path, str) else path
        if not pth.exists():
            return []
        str_pth = str(pth)
        return [name for name in os.listdir(str_pth) if os.path.isfile(os.path.join(str_pth, name))]

    def _get_directory_names(self, path: str) -> List[str]:
        """Get the directory names in the specified path."""
        omits = {"bin", "lib", "include", "__pycache__"}
        return [name for name in os.listdir(path) if name not in omits and os.path.isdir(os.path.join(path, name))]

    def _save_changed(
        self,
        pkg: str,
        pth: str,
        changes: dict,
        # before_files: List[str],
        # before_bin_files: List[str],
        # after_files: List[str],
        # after_bin_files: List[str],
        # before_dirs: List[str],
        # after_dirs: List[str],
    ) -> None:
        """Save the new directory names to a JSON file."""

        def _create_json() -> str:
            """Create a JSON file with the file names."""
            after_dirs: List[str] = changes.get("after_dirs", [])
            before_dirs: List[str] = changes.get("before_dirs", [])

            after_files: List[str] = changes.get("after_files", [])
            before_files: List[str] = changes.get("before_files", [])

            after_bin_files: List[str] = changes.get("after_bin_files", [])
            before_bin_files: List[str] = changes.get("before_bin_files", [])

            after_lib_files: List[str] = changes.get("after_lib_files", [])
            before_lib_files: List[str] = changes.get("before_lib_files", [])

            after_inc_files: List[str] = changes.get("after_inc_files", [])
            before_inc_files: List[str] = changes.get("before_inc_files", [])

            new_dirs = list(set(after_dirs) - set(before_dirs))
            new_files = list(set(after_files) - set(before_files))
            new_bin_files = list(set(after_bin_files) - set(before_bin_files))
            new_lib_files = list(set(after_lib_files) - set(before_lib_files))
            new_inc_files = list(set(after_inc_files) - set(before_inc_files))

            try:
                pkg_version = self.get_package_version(pkg)
            except Exception as e:
                self._logger.error("Error getting package version for '%s': %s", pkg, e)
                pkg_version = ""

            data = {
                "id": f"{self._config.oxt_name}_pip_pkg",
                "type_id": "pkg_tracker",
                "package": pkg,
                "package_version": pkg_version,
                "version": self._config.extension_version,
                "data": {
                    "new_dirs": new_dirs,
                    "new_files": new_files,
                    "new_bin_files": new_bin_files,
                    "new_lib_files": new_lib_files,
                    "new_inc_files": new_inc_files,
                },
            }
            return json.dumps(data, indent=4)

        try:
            json_str = _create_json()
            json_path = os.path.join(pth, f"{self._config.lo_implementation_name}_{pkg}.json")
            with open(json_path, "w") as f:
                f.write(json_str)
            self._logger.info("New directories and files saved to %s", json_path)
        except Exception as e:
            self._logger.exception("Error saving new directories and files: %s", e)

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
        j_contents = {}
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                j_contents = json.load(f)
                data = j_contents.get("data", {})
                if "bin" not in data:
                    data["bin"] = []

        return j_contents

    # check and see if there are any directories and files that need to be removed. Us the Json file to get the data
    def _remove_changed(self, pth: str, pkg: str) -> None:
        """Remove the new directories and files."""
        data_dict = self._get_json_data(pth, pkg)
        data: Dict[str, str] = data_dict.get("data", {})
        new_dirs = set(data.get("new_dirs", []))
        if "bin" in new_dirs:
            new_dirs.remove("bin")

        for d in new_dirs:
            dir_path = os.path.join(pth, d)
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    self._logger.debug("_remove_changed() Removed directory: %s", d)
                else:
                    self._logger.debug("_remove_changed() Directory %s does not exist.", d)
            except Exception as e:
                self._logger.error("_remove_changed() Error removing directory %s: %s", d, e)

        new_files = data.get("new_files", [])
        for f in new_files:
            file_path = Path(pth, f)
            try:
                if os.path.exists(file_path):
                    file_path.unlink()
                    self._logger.debug("_remove_changed() Removed file: %s", f)
                else:
                    self._logger.debug("_remove_changed() File %s does not exist.", f)
            except Exception as e:
                self._logger.error("_remove_changed() Error removing file %s: %s", f, e)

        new_files = data.get("new_bin_files", [])
        for f in new_files:
            file_path = Path(pth, "bin", f)
            try:
                if file_path.exists():
                    file_path.unlink()
                    self._logger.debug("_remove_changed() Removed file from bin: %s", f)
                else:
                    self._logger.debug("_remove_changed() File %s does not exist in bin.", f)
            except Exception as e:
                self._logger.error("_remove_changed() Error removing file %s from bin: %s", f, e)

        new_files = data.get("new_lib_files", [])
        for f in new_files:
            file_path = Path(pth, "lib", f)
            try:
                if file_path.exists():
                    file_path.unlink()
                    self._logger.debug("_remove_changed() Removed file from lib: %s", f)
                else:
                    self._logger.debug("_remove_changed() File %s does not exist in lib.", f)
            except Exception as e:
                self._logger.error("_remove_changed() Error removing file %s from lib: %s", f, e)

        new_files = data.get("new_inc_files", [])
        for f in new_files:
            file_path = Path(pth, "include", f)
            try:
                if file_path.exists():
                    file_path.unlink()
                    self._logger.debug("_remove_changed() Removed file from include: %s", f)
                else:
                    self._logger.debug("_remove_changed() File %s does not exist in include.", f)
            except Exception as e:
                self._logger.error("_remove_changed() Error removing file %s from include: %s", f, e)

        self._logger.info("_remove_changed() Removed new directories and files.")

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
    def no_pip_remove(self) -> Set[str]:
        return self._no_pip_remove

    @property
    def no_pip_install(self) -> Set[str]:
        return self._no_pip_install
