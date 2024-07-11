from __future__ import annotations
import os
import sys
import subprocess
from typing import Any, Dict, List, Tuple


# import pkg_resources
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

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
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env(), startupinfo=STARTUP_INFO
            )
        else:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._get_env())

        result = False
        if process.returncode == 0:
            self._logger.info(msg)
            result = True
        else:
            self._logger.error(err_msg)
            try:
                self._logger.error(process.stderr.decode("utf-8"))
            except Exception as err:
                self._logger.error(f"Error decoding stderr: {err}")

        if progress:
            self._logger.debug("Ending Progress Window")
            progress.kill()

        return result

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
        if rules_pass == False:
            self._logger.info(
                f"Package {name} {pkg_ver} already installed. It does not meet requirements specified by: {ver}, but will be upgraded."
            )
            return 0, rules
        if not force:
            self._logger.info(
                f"Package {name} {pkg_ver} already installed; However, it does not need to be installed to meet constraints: {ver}. It will be skipped."
            )
        return 1, rules

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
