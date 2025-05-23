# coding: utf-8
# region Imports
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set, TYPE_CHECKING, Union
import uno
import os
import sys
import platform
import site

from .oxt_logger.logger_config import LoggerConfig
from .meta.singleton import Singleton
from .basic_config import BasicConfig
from .oxt_logger.oxt_logger import OxtLogger

if TYPE_CHECKING:
    from .lo_util import Session
    from .lo_util import Util  # noqa: F401
    from .info import ExtensionInfo
    from .settings.general_settings import GeneralSettings  # noqa: F401
    from .settings.lp_settings import LpSettings
# endregion Imports


# region Constants

OS = platform.system()
IS_WIN = OS == "Windows"
IS_MAC = OS == "Darwin"
IS_LINUX = OS == "Linux"

# endregion Constants

# region Config Class


class Config(metaclass=Singleton):
    """
    Singleton Configuration Class

    Generally speaking this class is only used internally.
    """

    # region Init

    def __init__(self) -> None:
        if not TYPE_CHECKING:
            from .lo_util import Session
            from .info import ExtensionInfo
            from .lo_util import Util
            from .settings.general_settings import GeneralSettings
            from .settings.lp_settings import LpSettings

        logger_config = LoggerConfig()
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("Initializing Config")
        try:
            self._log_file = logger_config.log_file
            self._log_name = logger_config.log_name
            self._log_format = logger_config.log_format
            self._basic_config = BasicConfig()
            self._logger.debug("Basic config initialized")
            generals_settings = GeneralSettings()
            self._lp_settings = LpSettings()
            self._logger.debug("General Settings initialized")
            self._url_pip = generals_settings.url_pip
            self._pip_wheel_url = generals_settings.pip_wheel_url
            self._test_internet_url = generals_settings.test_internet_url
            self._log_pip_installs = generals_settings.log_pip_installs
            self._show_progress = generals_settings.show_progress
            self._startup_event = generals_settings.startup_event
            self._delay_startup = generals_settings.delay_startup

            self._session = Session()
            self._extension_info = ExtensionInfo()
            self._auto_install_in_site_packages = self._basic_config.auto_install_in_site_packages
            if not self._auto_install_in_site_packages and os.getenv("DEV_CONTAINER", "") == "1":
                # if running in a dev container (Codespace)
                self._auto_install_in_site_packages = True
            self._log_level = logger_config.log_level
            self._os = platform.system()
            self._is_win = IS_WIN
            self._is_mac = IS_MAC
            self._is_linux = IS_LINUX
            self._is_app_image = bool(os.getenv("APPIMAGE", ""))
            self._is_flatpak = bool(os.getenv("FLATPAK_ID", ""))
            self._is_snap = bool(os.getenv("SNAP_INSTANCE_NAME", ""))
            self._site_packages = ""
            util = Util()

            # self._package_location = Path(file_util.get_package_location(self._lo_identifier, True))
            self._package_location = Path(self._extension_info.get_extension_loc(self.lo_identifier, True)).resolve()
            self._package_name = self._package_location.stem
            self._python_major_minor = self._get_python_major_minor()

            self._is_user_installed = False
            self._is_shared_installed = False
            self._is_bundled_installed = False
            self._set_extension_installs()

            if self._is_win:
                self._python_path = Path(self.join(util.config("Module"), "python.exe"))
                self._site_packages = self._get_windows_site_packages_dir()
            elif self._is_mac:
                self._python_path = Path(self.join(util.config("Module"), "..", "Resources", "python")).resolve()
                self._site_packages = self._get_mac_site_packages_dir()
            elif self._is_app_image:
                self._python_path = Path(self.join(util.config("Module"), "python"))
                self._site_packages = self._get_default_site_packages_dir()
            else:
                self._python_path = self.get_path_default()  # Path(sys.executable)
                if self._is_flatpak:
                    self._site_packages = self._get_flatpak_site_packages_dir()
                else:
                    self._site_packages = self._get_default_site_packages_dir()
            self._logger.debug(f"Python Path: {self._python_path}")
        except Exception as err:
            self._logger.error(f"Error initializing config: {err}", exc_info=True)
            raise
        self._logger.debug("Config initialized")

    # endregion Init

    # region Methods
    def get_path_default(self) -> Path:
        # sys.executable is not reliable if working in an embedded python environment. My suggestions is to deduce it from os.__file__
        # https://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
        # try and find path from os
        # uno.__file__ is also a good candidate and usually exist in the program directory.
        p = self.find_program_directory(uno.__file__)
        if p is None:
            p = self.find_program_directory(os.__file__)
        if p is None:
            return Path(sys.executable)
        pp = p / "python"
        if pp.exists() and pp.is_file():
            return pp
        pp = p / "bin" / "python"
        if pp.exists() and pp.is_file():
            return pp
        return Path(sys.executable)

    def find_program_directory(self, start_path: str) -> Union[Path, None]:
        path = Path(start_path)
        for parent in path.parents:
            if parent.name == "program":
                return parent
        return None

    def join(self, *paths: str):
        return str(Path(paths[0]).joinpath(*paths[1:]))

    def _set_extension_installs(self) -> None:
        details = self._extension_info.get_extension_details(self.lo_identifier)
        if details[0] is not None:
            self._is_user_installed = True
        if details[1] is not None:
            self._is_shared_installed = True
        if details[2] is not None:
            self._is_bundled_installed = True

    def _get_python_major_minor(self) -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}"

    def _get_shared_site_packages_dir(self) -> Path:
        # sourcery skip: class-extract-method
        packages = site.getsitepackages()
        for pkg in packages:
            if pkg.endswith("site-packages"):
                return Path(pkg).resolve()
        for pkg in packages:
            if pkg.endswith("dist-packages"):
                return Path(pkg).resolve()
        return Path(packages[0]).resolve()

    def _get_default_site_packages_dir(self) -> str:
        if self.is_shared_installed or self.is_bundled_installed:
            # if package has been installed for all users (root)
            site_packages = self._get_shared_site_packages_dir()
        else:
            if site.USER_SITE:
                site_packages = Path(site.USER_SITE).resolve()
            else:
                site_packages = Path.home() / f".local/lib/python{self.python_major_minor}/site-packages"
            site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    def _get_flatpak_site_packages_dir(self) -> str:
        # should never be all users
        sand_box = os.getenv("FLATPAK_SANDBOX_DIR", "") or str(
            Path.home() / ".var/app/org.libreoffice.LibreOffice/sandbox"
        )
        site_packages = Path(sand_box) / f"lib/python{self.python_major_minor}/site-packages"
        site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    def _get_mac_site_packages_dir(self) -> str:
        # sourcery skip: class-extract-method
        if self.is_shared_installed or self.is_bundled_installed:
            # if package has been installed for all users (root)
            site_packages = self._get_shared_site_packages_dir()
        else:
            if site.USER_SITE:
                site_packages = Path(site.USER_SITE).resolve()
            else:
                site_packages = (
                    Path.home() / f"Library/LibreOfficePython/{self.python_major_minor}/lib/python/site-packages"
                )
            site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    def _get_windows_site_packages_dir(self) -> str:
        # sourcery skip: class-extract-method
        if self.is_shared_installed or self.is_bundled_installed:
            # if package has been installed for all users (root)
            site_packages = self._get_shared_site_packages_dir()
        else:
            if site.USER_SITE:
                site_packages = Path(site.USER_SITE).resolve()
            else:
                site_packages = (
                    Path.home() / f"'/AppData/Roaming/Python/Python{self.python_major_minor}/site-packages'"
                )
            site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    # endregion Methods

    # region Properties
    @property
    def basic_config(self) -> BasicConfig:
        """
        Gets the basic config.
        """
        return self._basic_config

    @property
    def author_names(self) -> List[str]:
        """
        Gets the list of author names.

        The value for this property can be set in pyproject.toml (tool.poetry.authors)

        This is the list of author names for the extension.
        """
        return self.basic_config.author_names

    @property
    def delay_startup(self) -> bool:
        """
        Gets the flag indicating if the startup should be delayed.
        """
        return self._delay_startup

    @property
    def default_locale(self) -> List[str]:
        """
        Gets the default locale such as ``['en', 'US']``.

        The value for this property can be set in pyproject.toml (tool.oxt.config.default_locale)

        This is the default locale to use if the locale is not set in the LibreOffice configuration.
        """
        return self._basic_config.default_locale

    @property
    def default_locale_str(self) -> str:
        """
        Gets the default locale as string separated by ``-`` such as ``en-US``.

        The value for this property can be set in pyproject.toml (tool.oxt.config.default_locale)

        This is the default locale to use if the locale is not set in the LibreOffice configuration.
        """
        return "-".join(self.default_locale)

    @property
    def url_pip(self) -> str:
        """
        String path such as ``https://bootstrap.pypa.io/get-pip.py``

        The value for this property can be set in pyproject.toml (tool.oxt.token.url_pip)
        """
        return self._url_pip
        # return self._basic_config.url_pip

    @property
    def test_internet_url(self) -> str:
        """
        String path such as ``https://www.google.com``

        The value for this property can be set in pyproject.toml (tool.oxt.token.test_internet_url)
        """
        return self._test_internet_url

    @property
    def python_path(self) -> Path:
        """
        Gets the path to the python executable.

        For some strange reason, on windows, the path can come back as 'soffice.bin' for 'sys.executable'.
        """
        return self._python_path

    @property
    def log_file(self) -> str:
        """
        Gets the name of the log file.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_file)
        """
        return self._log_file

    @property
    def log_name(self) -> str:
        """
        Gets the name of the log file.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_name)
        """
        return self._log_name

    @property
    def log_level(self) -> int:
        """
        Gets the log level.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_level)
        """
        return self._log_level

    @property
    def log_format(self) -> str:
        """
        Gets the log format.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_format)
        """
        return self._log_format

    @property
    def py_pkg_dir(self) -> str:
        """
        Gets the name of the directory where python packages are installed as a zip.

        The value for this property can be set in pyproject.toml (tool.oxt.token.py_pkg_dir)
        """
        return self._basic_config.py_pkg_dir

    @property
    def requirements(self) -> Dict[str, str]:
        """
        Gets the set of requirements.

        The value for this property can be set in pyproject.toml (tool.oxt.requirements)

        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._basic_config.requirements

    @property
    def zipped_preinstall_pure(self) -> bool:
        """
        Gets the flag indicating if pure python packages are be zipped.

        The value for this property can be set in pyproject.toml (tool.oxt.config.zip_preinstall_pure)

        If this is set to ``True`` then pure python packages will be zipped and installed as a zip file.
        """
        return self._basic_config.zipped_preinstall_pure

    @property
    def run_imports_linux(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension on Linux.
        The value for this property can be set in pyproject.toml (tool.oxt.config.run_imports_linux)
        """
        return self._basic_config.run_imports_linux

    @property
    def run_imports_macos(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension on macOS.
        The value for this property can be set in pyproject.toml (tool.oxt.config.run_imports_macos)
        """
        return self._basic_config.run_imports_macos

    @property
    def run_imports_win(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension on Windows.
        The value for this property can be set in pyproject.toml (tool.oxt.config.run_imports_win)
        """
        return self._basic_config.run_imports_win

    @property
    def auto_install_in_site_packages(self) -> bool:
        """
        Gets the flag indicating if packages are installed in the site-packages directory set in this config.

        The value for this property can be set in pyproject.toml (tool.oxt.config.auto_install_in_site_packages)

        If this is set to ``True`` then packages will be installed in the site-packages directory if this config has the value set.

        Flatpak ignores this setting and always installs packages in the site-packages directory determined in this config.

        Note:
            When running in a dev container (Codespace), this value is always set to ``True``.
        """
        return self._auto_install_in_site_packages

    @property
    def dialog_desktop_owned(self) -> bool:
        """
        Gets the flag indicating if the dialog is owned by LibreOffice desktop window.

        The value for this property can be set in pyproject.toml (tool.oxt.config.dialog_desktop_owned)

        If this is set to ``True`` then the dialog is owned by the LibreOffice desktop window.
        """
        return self._basic_config.dialog_desktop_owned

    @property
    def is_linux(self) -> bool:
        """
        Gets the flag indicating if the operating system is Linux.
        """
        return self._is_linux

    @property
    def is_mac(self) -> bool:
        """
        Gets the flag indicating if the operating system is macOS.
        """
        return self._is_mac

    @property
    def is_win(self) -> bool:
        """
        Gets the flag indicating if the operating system is Windows.
        """
        return self._is_win

    @property
    def is_app_image(self) -> bool:
        """
        Gets the flag indicating if LibreOffice is running as an AppImage.
        """
        return self._is_app_image

    @property
    def is_flatpak(self) -> bool:
        """
        Gets the flag indicating if LibreOffice is running as a Flatpak.
        """
        return self._is_flatpak

    @property
    def is_snap(self) -> bool:
        """
        Gets the flag indicating if LibreOffice is running as a Snap.
        """
        return self._is_snap

    @property
    def is_user_installed(self) -> bool:
        """
        Gets the flag indicating if extension is installed as user.
        """
        return self._is_user_installed

    @property
    def is_shared_installed(self) -> bool:
        """
        Gets the flag indicating if extension is installed as shared.
        """
        return self._is_shared_installed

    @property
    def is_bundled_installed(self) -> bool:
        """
        Gets the flag indicating if extension is installed bundled with LibreOffice.
        """
        return self._is_bundled_installed

    @property
    def os(self) -> str:
        """
        Gets the operating system.
        """
        return self._os

    @property
    def pip_wheel_url(self) -> str:
        """
        Gets the pip wheel url.

        May be empty string.
        """
        return self._pip_wheel_url

    @property
    def install_on_no_uninstall_permission(self) -> bool:
        """
        Gets the flag indicating if a package cannot be uninstalled due to permission error,
        then it will be installed anyway. This is usually the case when a package is installed
        in the system packages folder.
        """
        return self._basic_config.install_on_no_uninstall_permission

    @property
    def install_wheel(self) -> bool:
        """
        Gets the flag indicating if wheel should be installed.
        """
        return self._basic_config.install_wheel

    @property
    def lo_identifier(self) -> str:
        """
        Gets the LibreOffice identifier, such as, ``org.openoffice.extensions.ooopip``

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_identifier)
        """
        return self._basic_config.lo_identifier

    @property
    def lo_implementation_name(self) -> str:
        """
        Gets the LibreOffice implementation name, such as ``OooPipRunner``

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_implementation_name)
        """
        return self._basic_config.lo_implementation_name

    @property
    def python_major_minor(self) -> str:
        """
        Gets the python major minor version, such as ``3.9``
        """
        return self._python_major_minor

    @property
    def site_packages(self) -> str:
        """
        Gets the path to the site-packages directory. May be empty string.
        """
        return self._site_packages

    @property
    def session(self) -> Session:
        """
        Gets the LibreOffice session info.
        """
        return self._session

    @property
    def package_location(self) -> Path:
        """
        Gets the LibreOffice package location.
        """
        return self._package_location

    @property
    def package_name(self) -> str:
        """
        Gets the LibreOffice package name minus the ``.oxt`` extension.
        This value is derived from the package location.
        """
        return self._package_name

    @property
    def extension_info(self) -> ExtensionInfo:
        """
        Gets the LibreOffice extension info.
        """
        return self._extension_info

    @property
    def log_pip_installs(self) -> bool:
        """
        Gets the flag indicating if pip installs should be logged.
        """
        return self._log_pip_installs

    @property
    def log_indent(self) -> int:
        """
        Gets the amount of logging indent. ``0`` is no indent.

        The value for this property can be set in pyproject.toml (tool.oxt.config.log_indent)
        """
        return self._basic_config.log_indent

    @property
    def has_locals(self) -> bool:
        """
        Gets the flag indicating if the extension has local pip files to install.
        """
        return self._basic_config.has_locals

    @property
    def resource_dir_name(self) -> str:
        """
        Gets the resource directory name.

        The value for this property can be set in pyproject.toml (tool.oxt.config.resource_dir_name)

        This is the name of the directory containing the resource files.
        """
        return self._basic_config.resource_dir_name

    @property
    def resource_properties_prefix(self) -> str:
        """
        Gets the resource properties prefix.

        The value for this property can be set in pyproject.toml (tool.oxt.config.resource_properties_prefix)

        This is the prefix for the resource properties.
        """
        return self._basic_config.resource_properties_prefix

    @property
    def show_progress(self) -> bool:
        """
        Gets the flag indicating if the terminal should be shown.
        """
        return self._show_progress

    @property
    def startup_event(self) -> str:
        """
        Gets the startup event of the extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.startup_event)
        """
        return self._startup_event

    @property
    def uninstall_on_update(self) -> bool:
        """
        Gets the flag indicating if python packages should be uninstalled before updating.
        """
        return self.basic_config.uninstall_on_update

    @property
    def unload_after_install(self) -> bool:
        """
        Gets the flag indicating if the extension installer should unload after installation.
        """
        return self.basic_config.unload_after_install

    @property
    def window_timeout(self) -> int:
        """
        Gets the window timeout value.

        The value for this property can be set in pyproject.toml (tool.oxt.config.window_timeout)

        This is the number of seconds to wait for the LibreOffice window to start before installing packages without requiring a LibreOffice window.
        """
        return self._basic_config.window_timeout

    @property
    def isolate_windows(self) -> Set[str]:
        """
        Gets the list of package that are to  be installed in 32 or 64 bit locations.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.windows)
        """
        return self._basic_config.isolate_windows

    @property
    def no_pip_remove(self) -> Set[str]:
        """
        Gets the pip packages that are not allowed to be removed.

        The value for this property can be set in pyproject.toml (tool.oxt.config.no_pip_remove)

        This is the packages that are not allowed to be removed by the installer.
        """
        return self._basic_config.no_pip_remove

    @property
    def sym_link_cpython(self) -> bool:
        """
        Gets the flag indicating if CPython files should be symlinked on Linux AppImage and Mac OS.

        The value for this property can be set in pyproject.toml (tool.oxt.config.sym_link_cpython)

        If this is set to ``True`` then CPython will be symlinked on Linux AppImage and Mac OS.
        """
        return self._basic_config.sym_link_cpython

    @property
    def require_install_name_match(self) -> bool:
        """
        Gets the flag indicating if the package name must match the install name.
        """
        return self._basic_config.require_install_name_match

    @property
    def run_imports(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.run_imports)
        """
        return self._basic_config.run_imports

    @property
    def run_imports2(self) -> Set[str]:
        """
        Gets the set of imports that are required to run the seconded level of this extension.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.run_imports2)
        """
        return self._basic_config.run_imports2

    @property
    def extension_version(self) -> str:
        """
        Gets extension version.

        The value for this property can be set in pyproject.toml (tool.poetry.version)
        """
        return self._basic_config.extension_version

    @property
    def extension_license(self) -> str:
        """
        Gets extension license.

        The value for this property can be set in pyproject.toml (tool.poetry.license)
        """
        return self._basic_config.extension_license

    @property
    def extension_display_name(self) -> str:
        """
        Gets extension display Name.

        The value for this property can be set in pyproject.toml (tool.token.display_name)
        """
        return self._basic_config.extension_display_name

    @property
    def macro_lp_sheet_ctl_click(self) -> str:
        """
        Gets macro name of the sheet control click.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.macro_lp_sheet_ctl_click)
        """
        return self._basic_config.macro_lp_sheet_ctl_click

    @property
    def macro_sheet_on_calculate(self) -> str:
        """
        Gets macro name of for the sheet OnCalculate event.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.macro_sheet_on_calculate)
        """
        return self._basic_config.macro_sheet_on_calculate

    @property
    def oxt_name(self) -> str:
        """
        Gets the Oxt name of the extension without the ``.oxt`` extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.oxt_name)
        """
        return self._basic_config.oxt_name

    @property
    def flatpak_libre_pythonista_py_editor(self) -> str:
        """
        Gets the flatpak LibrePythonista python editor such as ``io.github.amourspirit.LibrePythonista_PyEditor``.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.flatpak_libre_pythonista_py_editor)
        """
        return self._basic_config.flatpak_libre_pythonista_py_editor

    @property
    def flatpak_libre_pythonista_py_editor_cell_cmd(self) -> str:
        """
        Gets the flatpak LibrePythonista python editor cell command such as ``cell_edit``.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.flatpak_libre_pythonista_py_editor_cell_cmd)
        """
        return self._basic_config.flatpak_libre_pythonista_py_editor_cell_cmd

    @property
    def flatpak_libre_pythonista_py_editor_install_url(self) -> str:
        """
        Gets the flatpak LibrePythonista python editor install instructions url.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.flatpak_libre_pythonista_py_editor_install_url)
        """
        return self._basic_config.flatpak_libre_pythonista_py_editor_install_url

    @property
    def lo_pip_dir(self) -> str:
        """
        Gets the Main Library directory name for this extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_pip)
        """
        return self._basic_config.lo_pip_dir

    @property
    def cmd_clean_file_prefix(self) -> str:
        """
        Gets the command clean file prefix.

        The value for this property can be set in pyproject.toml (tool.oxt.config.cmd_clean_file_prefix)
        """
        return self._basic_config.cmd_clean_file_prefix

    @property
    def pip_shared_dirs(self) -> List[str]:
        """
        Gets the list of shared directories for pip packages.
        These are used to build the cleanup scripts.

        The value for this property can be set in pyproject.toml (tool.oxt.config.pip_shared_dirs)
        """
        return self._basic_config.pip_shared_dirs

    # region tool.libre_pythonista.config
    @property
    def calc_props_json_name(self) -> str:
        """
        Gets the The name of the file that stores the json properties for the extension.
        This property value is typically prepended with ``general_code_name`` property.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._basic_config.calc_props_json_name

    @property
    def cell_cp_prefix(self) -> str:
        """
        Gets the custom property prefix for cells.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._basic_config.cell_cp_prefix

    @property
    def cell_cp_codename(self) -> str:
        """
        Gets the custom property code name for cells.

        The value for this property is generated in the build process.
        """
        return self._basic_config.cell_cp_codename

    @property
    def general_code_name(self) -> str:
        """
        Gets the General code name for the extension. This is a code safe name and can be use in var names.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._basic_config.general_code_name

    @property
    def lp_default_log_format(self) -> str:
        """
        Gets the default log format for the extension.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._basic_config.lp_default_log_format

    @property
    def lp_code_dir(self) -> str:
        """
        Gets name of the directory where LibrePythonista code is stored.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._basic_config.lp_code_dir

    @property
    def py_script_sheet_ctl_click(self) -> str:
        """
        Gets python Script name including the ``.py`` extension.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.py_script_sheet_ctl_click)
        """
        return self._basic_config.py_script_sheet_ctl_click

    @property
    def py_script_sheet_on_calculate(self) -> str:
        """
        Gets python Script name including the ``.py`` extension.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.py_script_sheet_on_calculate)
        """
        return self._basic_config.py_script_sheet_on_calculate

    @property
    def lp_py_cell_edit_sock_timeout(self) -> int:
        """
        Gets the LibrePythonista python cell edit socket timeout.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.lp_py_cell_edit_sock_timeout)
        """
        return self._basic_config.lp_py_cell_edit_sock_timeout

    @property
    def libreoffice_debug_port(self) -> int:
        """
        Gets the LibreOffice debug port.

        The value for this property can be set in pyproject.toml (tool.oxt.token.libreoffice_debug_port)
        """
        return self._basic_config.libreoffice_debug_port

    @property
    def lp_debug_port(self) -> int:
        """
        Gets the LibrePythonista debug port.

        The value for this property can be set in pyproject.toml (tool.oxt.token.lp_debug_port)
        """
        return self._basic_config.lp_debug_port

    # endregion tool.libre_pythonista.config
    @property
    def lp_settings(self) -> LpSettings:
        """
        Gets the LibrePythonista settings.
        """
        return self._lp_settings

    @property
    def debug_skip_events(self) -> Set[str]:
        """
        Gets the list of events to skip when debugging.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.debug_skip_events)
        """
        return self._basic_config.debug_skip_events

    # endregion Properties


# endregion Config Class
