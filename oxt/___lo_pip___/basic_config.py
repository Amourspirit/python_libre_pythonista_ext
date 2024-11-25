from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set, cast
import json


class ConfigMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            root = Path(__file__).parent
            config_file = Path(root, "config.json")
            with open(config_file, "r") as file:
                data = json.load(file)

            cls._instance = super().__call__(**data)
        return cls._instance


class BasicConfig(metaclass=ConfigMeta):
    def __init__(self, **kwargs) -> None:
        self._author_names = cast(List[str], kwargs.get("author_names", []))
        self._py_pkg_dir = str(kwargs["py_pkg_dir"])
        self._lo_identifier = str(kwargs["lo_identifier"])
        self._lo_implementation_name = str(kwargs["lo_implementation_name"])
        self._zipped_preinstall_pure = bool(kwargs["zipped_preinstall_pure"])
        self._auto_install_in_site_packages = bool(
            kwargs["auto_install_in_site_packages"]
        )
        self._install_wheel = bool(kwargs["install_wheel"])
        self._has_locals = bool(kwargs["has_locals"])
        self._window_timeout = int(kwargs["window_timeout"])
        self._dialog_desktop_owned = bool(kwargs["dialog_desktop_owned"])
        self._default_locale = cast(List[str], (kwargs["default_locale"]))
        self._resource_dir_name = str(kwargs["resource_dir_name"])
        self._extension_display_name = str(kwargs["extension_display_name"])
        self._extension_version = str(kwargs["extension_version"])
        self._extension_license = str(kwargs["extension_license"])
        self._resource_properties_prefix = str(kwargs["resource_properties_prefix"])
        self._isolate_windows = set(kwargs["isolate_windows"])
        self._sym_link_cpython = bool(kwargs["sym_link_cpython"])
        self._uninstall_on_update = bool(kwargs["uninstall_on_update"])
        self._install_on_no_uninstall_permission = bool(
            kwargs["install_on_no_uninstall_permission"]
        )
        self._unload_after_install = bool(kwargs["unload_after_install"])
        self._log_indent = int(kwargs.get("log_indent", 0))
        self._run_imports = set(kwargs["run_imports"])
        self._run_imports2 = set(kwargs["run_imports2"])
        self._run_imports_linux = set(kwargs["run_imports_linux"])
        self._run_imports_macos = set(kwargs["run_imports_macos"])
        self._run_imports_win = set(kwargs["run_imports_win"])
        self._oxt_name = str(kwargs["oxt_name"])

        # region tool.libre_pythonista.config
        self._cell_cp_prefix = str(kwargs["cell_cp_prefix"])
        self._cell_cp_codename = str(kwargs["cell_cp_codename"])
        self._general_code_name = str(kwargs["general_code_name"])
        self._calc_props_json_name = str(kwargs["calc_props_json_name"])
        self._lp_code_dir = str(kwargs["lp_code_dir"])
        self._lp_default_log_format = str(kwargs["lp_default_log_format"])
        self._macro_lp_sheet_ctl_click = str(kwargs["macro_lp_sheet_ctl_click"])
        self._macro_sheet_on_calculate = str(kwargs["macro_sheet_on_calculate"])

        self._py_script_sheet_ctl_click = str(kwargs["py_script_sheet_ctl_click"])
        self._py_script_sheet_on_calculate = str(kwargs["py_script_sheet_on_calculate"])
        self._no_pip_remove = set(kwargs["no_pip_remove"])

        self._flatpak_libre_pythonista_py_editor = str(
            kwargs["flatpak_libre_pythonista_py_editor"]
        )
        self._flatpak_libre_pythonista_py_editor_cell_cmd = str(
            kwargs["flatpak_libre_pythonista_py_editor_cell_cmd"]
        )
        # endregion tool.libre_pythonista.config

        if "requirements" not in kwargs:
            kwargs["requirements"] = {}
        self._requirements: Dict[str, str] = dict(**kwargs["requirements"])
        if "requirements_linux" not in kwargs:
            kwargs["requirements_linux"] = {}
        self._requirements_linux: Dict[str, str] = dict(**kwargs["requirements_linux"])

        if "requirements_macos" not in kwargs:
            kwargs["requirements_macos"] = {}
        self._requirements_macos: Dict[str, str] = dict(**kwargs["requirements_macos"])

        if "requirements_win" not in kwargs:
            kwargs["requirements_win"] = {}
        self._requirements_win: Dict[str, str] = dict(**kwargs["requirements_win"])

        if "experimental_requirements_linux" not in kwargs:
            kwargs["experimental_requirements_linux"] = {}
        self._experimental_requirements_linux: Dict[str, str] = dict(
            **kwargs["experimental_requirements_linux"]
        )

        if "experimental_requirements_macos" not in kwargs:
            kwargs["experimental_requirements_macos"] = {}
        self._experimental_requirements_macos: Dict[str, str] = dict(
            **kwargs["experimental_requirements_macos"]
        )

        if "experimental_requirements_win" not in kwargs:
            kwargs["experimental_requirements_win"] = {}
        self._experimental_requirements_win: Dict[str, str] = dict(
            **kwargs["experimental_requirements_win"]
        )

        self._libreoffice_debug_port = int(kwargs.get("libreoffice_debug_port", 0))
        self._lp_debug_port = int(kwargs.get("lp_debug_port", 0))

    # region Properties
    @property
    def author_names(self) -> List[str]:
        """
        Gets the list of author names.

        The value for this property can be set in pyproject.toml (tool.poetry.authors)

        This is the list of author names for the extension.
        """
        return self._author_names

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
    def default_locale(self) -> List[str]:
        """
        Gets the default locale.

        The value for this property can be set in pyproject.toml (tool.oxt.config.default_locale)

        This is the default locale to use if the locale is not set in the LibreOffice configuration.
        """
        return self._default_locale

    @property
    def dialog_desktop_owned(self) -> bool:
        """
        Gets the flag indicating if the dialog is owned by LibreOffice desktop window.

        The value for this property can be set in pyproject.toml (tool.oxt.config.dialog_desktop_owned)

        If this is set to ``True`` then the dialog is owned by the LibreOffice desktop window.
        """
        return self._dialog_desktop_owned

    @property
    def experimental_requirements_linux(self) -> Dict[str, str]:
        """
        Gets the set of experimental requirements specific to Linux.
        The value for this property can be set in pyproject.toml (tool.oxt.requirements_linux)
        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._experimental_requirements_linux

    @property
    def experimental_requirements_macos(self) -> Dict[str, str]:
        """
        Gets the set of experimental requirements specific to Mac OS.
        The value for this property can be set in pyproject.toml (tool.oxt.requirements_macos)
        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._experimental_requirements_macos

    @property
    def experimental_requirements_win(self) -> Dict[str, str]:
        """
        Gets the set of experimental requirements specific to Windows.
        The value for this property can be set in pyproject.toml (tool.oxt.requirements_win)
        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._experimental_requirements_win

    @property
    def extension_display_name(self) -> str:
        """
        Gets extension display Name.

        The value for this property can be set in pyproject.toml (tool.token.display_name)
        """
        return self._extension_display_name

    @property
    def extension_license(self) -> str:
        """
        Gets extension license.

        The value for this property can be set in pyproject.toml (tool.poetry.license)
        """
        return self._extension_license

    @property
    def extension_version(self) -> str:
        """
        Gets extension version.

        The value for this property can be set in pyproject.toml (tool.poetry.version)
        """
        return self._extension_version

    @property
    def flatpak_libre_pythonista_py_editor(self) -> str:
        """
        Gets the flatpak LibrePythonista python editor such as ``io.github.amourspirit.LibrePythonista_PyEditor``.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.flatpak_libre_pythonista_py_editor)
        """
        return self._flatpak_libre_pythonista_py_editor

    @property
    def flatpak_libre_pythonista_py_editor_cell_cmd(self) -> str:
        """
        Gets the flatpak LibrePythonista python editor cell command such as ``cell_edit``.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config.flatpak_libre_pythonista_py_editor_cell_cmd)
        """
        return self._flatpak_libre_pythonista_py_editor_cell_cmd

    @property
    def has_locals(self) -> bool:
        """
        Gets the flag indicating if the extension has local pip files to install.
        """
        return self._has_locals

    @property
    def install_on_no_uninstall_permission(self) -> bool:
        """
        Gets the flag indicating if a package cannot be uninstalled due to permission error,
        then it will be installed anyway. This is usually the case when a package is installed
        in the system packages folder.
        """
        return self._install_on_no_uninstall_permission

    @property
    def install_wheel(self) -> bool:
        """
        Gets the flag indicating if wheel should be installed.
        """
        return self._install_wheel

    @property
    def isolate_windows(self) -> Set[str]:
        """
        Gets the list of package that are to  be installed in 32 or 64 bit locations.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.windows)
        """
        return self._isolate_windows

    @property
    def lo_identifier(self) -> str:
        """
        Gets the LibreOffice identifier, such as, ``org.openoffice.extensions.ooopip``

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_identifier)
        """
        return self._lo_identifier

    @property
    def libreoffice_debug_port(self) -> int:
        """
        Gets the LibreOffice debug port.

        The value for this property can be set in pyproject.toml (tool.oxt.token.libreoffice_debug_port)
        """
        return self._libreoffice_debug_port

    @property
    def lo_implementation_name(self) -> str:
        """
        Gets the LibreOffice implementation name, such as ``OooPipRunner``

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_implementation_name)
        """
        return self._lo_implementation_name

    @property
    def log_indent(self) -> int:
        """
        Gets the amount of logging indent. ``0`` is no indent.

        The value for this property can be set in pyproject.toml (tool.oxt.config.log_indent)
        """
        return self._log_indent

    @property
    def lp_code_dir(self) -> str:
        """
        Gets name of the directory where LibrePythonista code is stored.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._lp_code_dir

    @property
    def lp_debug_port(self) -> int:
        """
        Gets the LibrePythonista debug port.

        The value for this property can be set in pyproject.toml (tool.oxt.token.lp_debug_port)
        """
        return self._lp_debug_port

    @property
    def macro_lp_sheet_ctl_click(self) -> str:
        """
        Gets macro name of the sheet control click.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.macro_lp_sheet_ctl_click)
        """
        return self._macro_lp_sheet_ctl_click

    @property
    def macro_sheet_on_calculate(self) -> str:
        """
        Gets macro name of for the sheet OnCalculate event.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.macro_sheet_on_calculate)
        """
        return self._macro_sheet_on_calculate

    @property
    def no_pip_remove(self) -> Set[str]:
        """
        Gets the pip packages that are not allowed to be removed.

        The value for this property can be set in pyproject.toml (tool.oxt.config.no_pip_remove)

        This is the packages that are not allowed to be removed by the installer.
        """
        return self._no_pip_remove

    @property
    def oxt_name(self) -> str:
        """
        Gets the Otx name of the extension without the ``.otx`` extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.oxt_name)
        """
        return self._oxt_name

    @property
    def py_pkg_dir(self) -> str:
        """
        The value for this property can be set in pyproject.toml (tool.oxt.config.py_pkg_dir)
        """
        return self._py_pkg_dir

    @property
    def py_script_sheet_ctl_click(self) -> str:
        """
        Gets python Script name including the ``.py`` extension.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.py_script_sheet_ctl_click)
        """
        return self._py_script_sheet_ctl_click

    @property
    def py_script_sheet_on_calculate(self) -> str:
        """
        Gets python Script name including the ``.py`` extension.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.py_script_sheet_on_calculate)
        """
        return self._py_script_sheet_on_calculate

    @property
    def requirements(self) -> Dict[str, str]:
        """
        Gets the set of requirements.

        The value for this property can be set in pyproject.toml (tool.oxt.requirements)

        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._requirements

    @property
    def requirements_linux(self) -> Dict[str, str]:
        """
        Gets the set of requirements specific to Linux.
        The value for this property can be set in pyproject.toml (tool.oxt.requirements_linux)
        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._requirements_linux

    @property
    def requirements_macos(self) -> Dict[str, str]:
        """
        Gets the set of requirements specific to Mac OS.
        The value for this property can be set in pyproject.toml (tool.oxt.requirements_macos)
        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._requirements_macos

    @property
    def requirements_win(self) -> Dict[str, str]:
        """
        Gets the set of requirements specific to Windows.
        The value for this property can be set in pyproject.toml (tool.oxt.requirements_win)
        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._requirements_win

    @property
    def resource_dir_name(self) -> str:
        """
        Gets the resource directory name.

        The value for this property can be set in pyproject.toml (tool.oxt.config.resource_dir_name)

        This is the name of the directory containing the resource files.
        """
        return self._resource_dir_name

    @property
    def run_imports_linux(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension on Linux.
        The value for this property can be set in pyproject.toml (tool.oxt.config.run_imports_linux)
        """
        return self._run_imports_linux

    @property
    def run_imports_macos(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension on Mac OS.
        The value for this property can be set in pyproject.toml (tool.oxt.config.run_imports_macos)
        """
        return self._run_imports_macos

    @property
    def run_imports_win(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension on Windows.
        The value for this property can be set in pyproject.toml (tool.oxt.config.run_imports_win)
        """
        return self._run_imports_win

    @property
    def resource_properties_prefix(self) -> str:
        """
        Gets the resource properties prefix.

        The value for this property can be set in pyproject.toml (tool.oxt.config.resource_properties_prefix)

        This is the prefix for the resource properties.
        """
        return self._resource_properties_prefix

    @property
    def run_imports(self) -> Set[str]:
        """
        Gets the set of imports that are required to run this extension.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.run_imports)
        """
        return self._run_imports

    @property
    def run_imports2(self) -> Set[str]:
        """
        Gets the set of imports that are required to run the seconded level of this extension.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.run_imports2)
        """
        return self._run_imports2

    @property
    def sym_link_cpython(self) -> bool:
        """
        Gets the flag indicating if CPython files should be symlinked on Linux AppImage and Mac OS.

        The value for this property can be set in pyproject.toml (tool.oxt.config.sym_link_cpython)

        If this is set to ``True`` then CPython will be symlinked on Linux AppImage and Mac OS.
        """
        return self._sym_link_cpython

    @property
    def uninstall_on_update(self) -> bool:
        """
        Gets the flag indicating if python packages should be uninstalled before updating.
        """
        return self._uninstall_on_update

    @property
    def unload_after_install(self) -> bool:
        """
        Gets the flag indicating if the extension installer should unload after installation.
        """
        return self._unload_after_install

    @property
    def window_timeout(self) -> int:
        """
        Gets the window timeout value.

        The value for this property can be set in pyproject.toml (tool.oxt.config.window_timeout)

        This is the number of seconds to wait for the LibreOffice window to start before installing packages without requiring a LibreOffice window.
        """
        return self._window_timeout

    @property
    def zipped_preinstall_pure(self) -> bool:
        """
        Gets the flag indicating if pure python packages are be zipped.

        The value for this property can be set in pyproject.toml (tool.oxt.config.zip_preinstall_pure)

        If this is set to ``True`` then pure python packages will be zipped and installed as a zip file.
        """
        return self._zipped_preinstall_pure

    # region tool.libre_pythonista.config
    @property
    def calc_props_json_name(self) -> str:
        """
        Gets the The name of the file that stores the json properties for the extension.
        This property value is typically prepended with ``general_code_name`` property.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._calc_props_json_name

    @property
    def cell_cp_prefix(self) -> str:
        """
        Gets the custom property prefix for cells.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._cell_cp_prefix

    @property
    def cell_cp_codename(self) -> str:
        """
        Gets the custom property code name for cells.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._cell_cp_codename

    @property
    def general_code_name(self) -> str:
        """
        Gets the General code name for the extension. This is a code safe name and can be use in var names.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._general_code_name

    @property
    def lp_default_log_format(self) -> str:
        """
        Gets the default log format for the extension.

        The value for this property can be set in pyproject.toml (tool.libre_pythonista.config)
        """
        return self._lp_default_log_format

    # endregion tool.libre_pythonista.config

    # endregion Properties
