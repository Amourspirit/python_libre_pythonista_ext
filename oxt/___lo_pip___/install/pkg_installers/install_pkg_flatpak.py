from __future__ import annotations
import subprocess


# import pkg_resources
from ...oxt_logger import OxtLogger
from .install_pkg import InstallPkg
from ..progress import Progress
from .install_pkg import STARTUP_INFO


class InstallPkgFlatpak(InstallPkg):
    """Install pip packages for flatpak."""

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

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

        if not self.config.site_packages:
            self._logger.error(
                "No site-packages directory set in configuration. site_packages value should be set in lo_pip.config.py"
            )
            return False
        cmd = ["install"]
        if force:
            cmd.append("--force-reinstall")
        elif self.flag_upgrade:
            cmd.append("--upgrade")

        cmd.append(f"--target={self.config.site_packages}")

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
            msg = self.resource_resolver.resolve_string("msg08")
            title = self.resource_resolver.resolve_string("title01") or self.config.lo_implementation_name
            self._logger.debug("Starting Progress Window")
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

        if progress:
            self._logger.debug("Ending Progress Window")
            progress.kill()
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
            return True
        else:
            self._logger.error(err_msg)
        return False
