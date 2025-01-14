from __future__ import annotations
import contextlib
from typing import Any, cast, Dict, List, Tuple, TYPE_CHECKING
import os
import shutil
import threading
import re
import urllib.request
import urllib.error
from pathlib import Path
import json

from ooodev.loader import Lo
from ooodev.dialog.msgbox import (
    MessageBoxResultsEnum,
    MessageBoxType,
    MsgBox,
    MessageBoxButtonsEnum,
)

from ooodev.dialog.input import Input

# from ..dialog.user_input.input import Input
from ..dialog.py_pip.remote_dlg_input import RemoteDlgInput
from .pkg_info import PkgInfo


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.install.install_pkg import InstallPkg
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ....___lo_pip___.config import Config
    from ....___lo_pip___.install.download import Download
    from ....___lo_pip___.events.named_events import GenNamedEvent
    from ....___lo_pip___.events.lo_events import LoEvents
    from ....___lo_pip___.events.args.event_args import EventArgs
    from ....___lo_pip___.install.progress_window.progress_dialog_true import (
        ProgressDialogTrue,
    )
    from ....___lo_pip___.lo_util.target_path import TargetPath
    from ....___lo_pip___.install.progress import Progress
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.install.install_pkg import InstallPkg
    from ___lo_pip___.config import Config
    from ___lo_pip___.install.download import Download
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.events.named_events import GenNamedEvent
    from ___lo_pip___.events.lo_events import LoEvents
    from ___lo_pip___.events.args.event_args import EventArgs
    from ___lo_pip___.install.progress_window.progress_dialog_true import (
        ProgressDialogTrue,
    )
    from ___lo_pip___.lo_util.target_path import TargetPath
    from ___lo_pip___.install.progress import Progress


class InstallPipPkg:
    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._ctx = Lo.get_context()
        self._rr = ResourceResolver(self._ctx)
        self._config = Config()
        self._pk_info = PkgInfo()
        self._events = LoEvents()
        self._path_python = Path(self._config.python_path)
        self._target_path = TargetPath()
        if self._log.is_debug:
            self._log.debug(f"init() Python path: {self._path_python}")
        self._init_events()

    def _init_events(self) -> None:
        # By default no progress window will be displayed without this rule.
        # The display window is part of the original install process
        # and does not contains a rule that checks if the window is available.
        # This class is expected to be called only from the main window via dispatch command.
        # By hooking the event we can add the rule to the list of rules that will be checked.
        # This will allow a dialog progress window to be displayed.
        self._fn_on_progress_rules_event = self._on_progress_rules_event
        self._events.on(GenNamedEvent.PROGRESS_RULES_EVENT, self._fn_on_progress_rules_event)

    def _on_progress_rules_event(self, args: Any, event_arg: EventArgs) -> None:
        # add the ProgressDialogTrue rule to the rules list to get the progress dialog to display
        d_args = cast(Dict[str, Any], event_arg.event_data)
        rules = cast(list, d_args["rules"])
        rules.append(ProgressDialogTrue)

    def install(self) -> None:
        """Install pip packages."""
        self._log.debug("InstallPipPkg.install()")
        dlg = RemoteDlgInput()
        result = dlg.show()
        if result == MessageBoxResultsEnum.OK.value:
            if not self._is_internet_connected():
                MsgBox.msgbox(
                    self._rr.resolve_string("msg07"),
                    title=self._rr.resolve_string("msg01"),
                    boxtype=MessageBoxType.ERRORBOX,
                )
                self._log.warning("Internet not connected.")
                return
            pkg = dlg.package_name
            name, ver = self._parse_pip_install_string(pkg)
            if self._is_valid_pypi_package(name):
                self._log.debug(f"Package {name} is a valid PyPI package.")
            else:
                msg = self._rr.resolve_string("msg12").format(name)  # Package {} not found
                MsgBox.msgbox(
                    msg,
                    title=self._rr.resolve_string("msg01"),
                    boxtype=MessageBoxType.ERRORBOX,
                )
                self._log.warning(f"Package {name} not found.")
                return

            force_install = dlg.force_install
            self.log.debug(
                f"InstallPipPkg.install() Starting install Thread. Package: {name}, Version: {ver}, Force install: {force_install}"
            )
            thread = threading.Thread(target=self._install_pkg, args=(name, ver, force_install), daemon=True)
            thread.start()
        else:
            self._log.debug("User cancelled the install package operation.")
            return

    def uninstall(self) -> None:
        self._log.debug("InstallPipPkg.uninstall()")
        pkg_name = Input.get_input(
            title=self._rr.resolve_string("strPackageName"),
            msg=self._rr.resolve_string("strPackageNameUninstall"),
            ok_lbl=self._rr.resolve_string("dlg01"),
            cancel_lbl=self._rr.resolve_string("dlg02"),
        )
        self._log.debug(f"uninstall() Package name: {pkg_name}")
        pkg_name = pkg_name.strip()
        if not pkg_name:
            self._log.debug("uninstall() No input.")
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg008"),
                title=self._rr.resolve_string("mbtitle008"),
                boxtype=MessageBoxType.INFOBOX,
            )
            return
        if pkg_name in self._config.no_pip_remove:
            MsgBox.msgbox(
                self._rr.resolve_string("msg17").format(pkg_name),  # Package {} is protected and can not be removed
                title=self._rr.resolve_string("msg01"),
                boxtype=MessageBoxType.ERRORBOX,
            )
            self._log.info(f"Package {pkg_name} cannot be removed.")
            return
        if not self.is_package_installed(pkg_name):
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg010").format(pkg_name),  # Package {} is not installed
                title=self._rr.resolve_string("msg01"),  # Error
                boxtype=MessageBoxType.ERRORBOX,
            )
            self._log.info(f"Package {pkg_name} is not installed.")
            return
        # display a message box ask the user to confirm the uninstall
        result = MsgBox.msgbox(
            self._rr.resolve_string("msg18").format(pkg_name),  # Are your sure you want to remove {}
            title=self._rr.resolve_string("title14"),  # Confirm
            boxtype=MessageBoxType.QUERYBOX,
            buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
        )
        if result == MessageBoxResultsEnum.YES.value:
            # Run _un_install_pkg in a separate thread
            thread = threading.Thread(target=self._un_install_pkg, args=(pkg_name,), daemon=True)
            thread.start()

    def is_package_installed(self, pkg: str) -> bool:
        """Check if a package is installed."""
        return self._pk_info.is_package_installed(pkg)

    def _is_internet_connected(self) -> bool:
        """Check if the internet is connected."""
        return Download().check_internet_connection()

    def _parse_pip_install_string(self, pip_string: str) -> Tuple[str, str]:
        # Define the regex pattern to match the package name and version specifier
        pattern = r"^([a-zA-Z0-9\-_]+)(.*)$"

        if match := re.match(pattern, pip_string):
            # Extract the package name and the remaining string
            package_name = match.group(1)
            version_specifier = match.group(2).strip()
            if version_specifier:
                self._log.debug(
                    f"_parse_pip_install_string() Package name: {package_name}, Version specifier: {version_specifier}"
                )
            else:
                version_specifier = ""
                self._log.debug(f"_parse_pip_install_string() Package name: {package_name}, No version specifier)")
            result = package_name, version_specifier
        else:
            result = pip_string, ""
            self._log.debug(f"_parse_pip_install_string() Package name: {result[0]}, No version specifier")
        return result

    def _is_valid_pypi_package(self, pkg: str) -> bool:
        """Check if a package name is a valid PyPI package."""
        url = f"https://pypi.org/pypi/{pkg}/json"
        try:
            with urllib.request.urlopen(url) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise

    def _install_pkg(self, pkg: str, version: str, force: bool) -> None:
        """Install a package using pip."""
        self._log.debug(f"InstallPipPkg._install_pkg({pkg}, {version}, {force})")
        try:
            install = InstallPkg(ctx=self._ctx)
            result = install.install(req={pkg: version}, force=force)
            if result:
                self._post_install()
                MsgBox.msgbox(
                    self._rr.resolve_string("msg13").format(pkg),  # Package {} installed successfully
                    title=self._rr.resolve_string("title02"),
                    boxtype=MessageBoxType.INFOBOX,
                )
                self._log.info(f"Package {pkg} installed successfully.")
            else:
                MsgBox.msgbox(
                    self._rr.resolve_string("msg14").format(pkg),  # Package {} installation failed
                    title=self._rr.resolve_string("msg01"),
                    boxtype=MessageBoxType.ERRORBOX,
                )
                self._log.error(f"Package {pkg} installation failed.")
            self._log.debug("InstallPipPkg._install_pkg() completed.")
        except Exception as e:
            self._log.exception(f"Error installing package {pkg}: {e}")

    def _un_install_pkg(self, pkg: str) -> None:
        """Install a package using pip."""
        self._log.debug(f"InstallPipPkg._un_install_pkg({pkg})")
        install = InstallPkg(ctx=self._ctx)
        if install.uninstall(pkg, remove_tracking_file=True):
            MsgBox.msgbox(
                self._rr.resolve_string("msg15").format(pkg),  # Package {} removed successfully
                title=self._rr.resolve_string("title02"),
                boxtype=MessageBoxType.INFOBOX,
            )
            self._log.info(f"Package {pkg} removed successfully.")
        else:
            MsgBox.msgbox(
                self._rr.resolve_string("msg16").format(pkg),  # Package {} removal failed
                title=self._rr.resolve_string("msg01"),
                boxtype=MessageBoxType.ERRORBOX,
            )
            self._log.error(f"Package {pkg} removal failed.")
        self._log.debug("InstallPipPkg._un_install_pkg() completed.")

    def _post_install(self) -> None:
        self._log.debug("Post Install starting")
        if not self._config.sym_link_cpython:
            self._log.debug(
                "Not creating CPython link because configuration has it turned off. Skipping post install."
            )
            return
        if self._config.is_win:
            self._log.debug("Windows, skipping post install.")
            return
        progress: Progress | None = None
        try:
            if TYPE_CHECKING:
                from ....___lo_pip___.install.post.cpython_link import CPythonLink
            else:
                from ___lo_pip___.install.post.cpython_link import CPythonLink

            link = CPythonLink()
            if self._config.is_mac or self._config._is_app_image:
                self._log.debug("_post_install() Linking needed")
            else:
                # mac and app image are known to need linking.
                # There are rare cases that linking is still needed.
                # Such as when deb files are download directly from LibreOffice and installed.
                # In this case LibreOffice use an embedded python similar to AppImage
                self._log.debug("Not Mac or AppImage, checking if needs linking")

                if link.get_needs_linking():
                    self._log.debug("Linking needed.")
                else:
                    self._log.debug("No linking needed. Skipping post install.")
                    return
            if self._config.show_progress:
                msg = self._rr.resolve_string("msg19")
                title = self._rr.resolve_string("title03")
                progress = Progress(start_msg=msg, title=title)
                progress.start()
            link.link()
        except Exception as err:
            self._log.error(err, exc_info=True)
            return
        finally:
            if progress:
                progress.kill()
        self._log.debug("Post Install Done")

    @property
    def log(self) -> OxtLogger:
        return self._log
