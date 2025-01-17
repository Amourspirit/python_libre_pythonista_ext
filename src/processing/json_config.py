from __future__ import annotations
from typing import Any, cast, Dict, List
from pathlib import Path
import json
import toml

from ..meta.singleton import Singleton
from ..config import Config
from .token import Token


def has_whitespace(value: str) -> bool:
    return any(char.isspace() for char in value)


class JsonConfig(metaclass=Singleton):
    """Singleton Class the Config Json."""

    def __init__(self) -> None:
        self._config = Config()
        self._cfg = toml.load(self._config.toml_path)
        self._requirements = cast(Dict[str, str], self._cfg["tool"]["oxt"]["requirements"])

        try:
            self._zip_preinstall_pure = cast(bool, self._cfg["tool"]["oxt"]["config"]["zip_preinstall_pure"])
        except Exception:
            self._zip_preinstall_pure = False
        try:
            self._auto_install_in_site_packages = cast(
                bool,
                self._cfg["tool"]["oxt"]["config"]["auto_install_in_site_packages"],
            )
        except Exception:
            self._auto_install_in_site_packages = False
        try:
            self._install_wheel = cast(bool, self._cfg["tool"]["oxt"]["config"]["install_wheel"])
        except Exception:
            self._install_wheel = False
        try:
            self._window_timeout = int(self._cfg["tool"]["oxt"]["config"]["window_timeout"])
        except Exception:
            self._window_timeout = 5
        try:
            self._dialog_desktop_owned = cast(bool, self._cfg["tool"]["oxt"]["config"]["dialog_desktop_owned"])
        except Exception:
            self._dialog_desktop_owned = False

        try:
            self._default_locale = cast(list, self._cfg["tool"]["oxt"]["config"]["default_locale"])
        except Exception:
            self._default_locale = ["en", "US"]
        # resource_dir_name
        try:
            self._resource_dir_name = cast(str, self._cfg["tool"]["oxt"]["config"]["resource_dir_name"])
        except Exception:
            self._resource_dir_name = "resources"
        try:
            self._resource_properties_prefix = cast(
                str, self._cfg["tool"]["oxt"]["config"]["resource_properties_prefix"]
            )
        except Exception:
            self._resource_properties_prefix = "pipstrings"

        try:
            self._isolate_windows = cast(List[str], self._cfg["tool"]["oxt"]["isolate"]["windows"])
        except Exception:
            self._isolate_windows = []

        try:
            self._sym_link_cpython = cast(bool, self._cfg["tool"]["oxt"]["config"]["sym_link_cpython"])
        except Exception:
            self._sym_link_cpython = False
        try:
            self._uninstall_on_update = cast(bool, self._cfg["tool"]["oxt"]["config"]["uninstall_on_update"])
        except Exception:
            self._uninstall_on_update = True
        try:
            self._install_on_no_uninstall_permission = cast(
                bool,
                self._cfg["tool"]["oxt"]["config"]["install_on_no_uninstall_permission"],
            )
        except Exception:
            self._install_on_no_uninstall_permission = True

        try:
            self._unload_after_install = cast(bool, self._cfg["tool"]["oxt"]["config"]["unload_after_install"])
        except Exception:
            self._unload_after_install = True

        try:
            self._run_imports = cast(list, self._cfg["tool"]["oxt"]["config"]["run_imports"])
        except Exception:
            self._run_imports = []

        try:
            self._run_imports_linux = cast(list, self._cfg["tool"]["oxt"]["config"]["run_imports_linux"])
        except Exception:
            self._run_imports_linux = []

        try:
            self._run_imports_macos = cast(list, self._cfg["tool"]["oxt"]["config"]["run_imports_macos"])
        except Exception:
            self._run_imports_macos = []

        try:
            self._run_imports_win = cast(list, self._cfg["tool"]["oxt"]["config"]["run_imports_win"])
        except Exception:
            self._run_imports_win = []

        try:
            self._run_imports2 = cast(list, self._cfg["tool"]["oxt"]["config"]["run_imports2"])
        except Exception:
            self._run_imports2 = []

        try:
            self._log_indent = cast(int, self._cfg["tool"]["oxt"]["config"]["log_indent"])
        except Exception:
            self._log_indent = 0

        try:
            self._require_install_name_match = cast(
                bool, self._cfg["tool"]["oxt"]["config"]["require_install_name_match"]
            )
        except Exception:
            self._require_install_name_match = False

        # region tool.libre_pythonista.config
        try:
            self._cell_custom_prop_prefix = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["cell_custom_prop_prefix"],
            )
        except Exception:
            self._cell_custom_prop_prefix = "libre_pythonista_"

        try:
            self._cell_custom_prop_codename = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["cell_custom_prop_codename"],
            )
        except Exception:
            self._cell_custom_prop_codename = "codename"

        try:
            self._py_script_sheet_ctl_click = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["py_script_sheet_ctl_click"],
            )
        except Exception:
            self._py_script_sheet_ctl_click = "control_handler.py"

        try:
            self._py_script_sheet_on_calculate = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["py_script_sheet_on_calculate"],
            )
        except Exception:
            self._py_script_sheet_on_calculate = "share_event.py"

        try:
            self._general_codename = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["general_code_name"],
            )
        except Exception:
            self._general_codename = "libre_pythonista"

        try:
            self._calc_props_json_name = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["calc_props_json_name"],
            )
        except Exception:
            self._calc_props_json_name = "_calc_props.json"

        try:
            self._lp_code_dir = cast(str, self._cfg["tool"]["libre_pythonista"]["config"]["lp_code_dir"])
        except Exception:
            self._lp_code_dir = "librepythonista"

        try:
            self._lp_default_log_format = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["lp_default_log_format"],
            )
        except Exception:
            self._lp_default_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        try:
            self._macro_lp_sheet_ctl_click = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["macro_lp_sheet_ctl_click"],
            )
        except Exception:
            self._macro_lp_sheet_ctl_click = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        try:
            self._macro_sheet_on_calculate = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["macro_sheet_on_calculate"],
            )
        except Exception:
            self._macro_sheet_on_calculate = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        try:
            self._flatpak_libre_pythonista_py_editor = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["flatpak_libre_pythonista_py_editor"],
            )
        except Exception:
            self._flatpak_libre_pythonista_py_editor = "io.github.amourspirit.LibrePythonista_PyEditor"

        try:
            self._flatpak_libre_pythonista_py_editor_cell_cmd = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["flatpak_libre_pythonista_py_editor_cell_cmd"],
            )
        except Exception:
            self._flatpak_libre_pythonista_py_editor_cell_cmd = "cell_edit"

        try:
            self._flatpak_libre_pythonista_py_editor_install_url = cast(
                str,
                self._cfg["tool"]["libre_pythonista"]["config"]["flatpak_libre_pythonista_py_editor_install_url"],
            )
        except Exception:
            self._flatpak_libre_pythonista_py_editor_install_url = (
                "https://github.com/Amourspirit/LibrePythonista_PyEditor/wiki"
            )

        try:
            self._lp_py_cell_edit_sock_timeout = cast(
                int,
                self._cfg["tool"]["libre_pythonista"]["config"]["lp_py_cell_edit_sock_timeout"],
            )
        except Exception:
            self._lp_py_cell_edit_sock_timeout = 10
        # endregion tool.libre_pythonista.config

        try:
            self._extension_license = cast(str, self._cfg["project"]["license"])
        except Exception:
            self._extension_license = ""

        try:
            self._extension_version = cast(str, self._cfg["project"]["version"])
        except Exception:
            self._extension_license = ""

        try:
            self._author_names = self._get_author_names(self._cfg)
        except Exception:
            self._author_names = []

        try:
            self._no_pip_remove = cast(list, self._cfg["tool"]["oxt"]["config"]["no_pip_remove"])
        except Exception:
            self._no_pip_remove = ["pip", "setuptools", "wheel"]

        try:
            self._lp_debug_port = cast(int, self._cfg["tool"]["oxt"]["config"]["token"]["lp_debug_port"])
        except Exception:
            self._lp_debug_port = 5679

        try:
            self._cmd_clean_file_prefix = cast(
                str,
                self._cfg["tool"]["oxt"]["config"]["cmd_clean_file_prefix"],
            )
        except Exception:
            self._cmd_clean_file_prefix = ""

        try:
            self._pip_shared_dirs = cast(list, self._cfg["tool"]["oxt"]["config"]["pip_shared_dirs"])
        except Exception:
            self._pip_shared_dirs = ["bin", "lib", "include", "inc", "docs", "config"]

        # region Requirements Rule
        # Access a specific table
        try:
            self._py_packages = cast(List[Dict[str, str]], self._cfg["tool"]["oxt"]["py_packages"])
        except Exception:
            self._py_packages = []

        try:
            self._lp_editor_py_packages = cast(List[Dict[str, str]], self._cfg["tool"]["oxt"]["lp_editor_py_packages"])
        except Exception:
            self._lp_editor_py_packages = []
        # endregion Requirements Rule

        self._validate()
        self._warnings()

    def _get_author_names(self, cfg: Dict[str, Any]) -> List[str]:
        """Get the author names."""
        authors = cast(List[str], cfg["tool"]["poetry"]["authors"])
        # Author elements are in the format of: ":Barry-Thomas-Paul: Moss <4193389+Amourspirit@users.noreply.github.com>"
        # get the names
        author_names = []
        for author in authors:
            author_names.append(author.split("<")[0].strip())
        return author_names

    def update_json_config(self, json_config_path: Path) -> None:
        """Read and updates the config.json file."""
        with open(json_config_path, "r") as f:
            json_config = json.load(f)
        token = Token()
        json_config["py_pkg_dir"] = token.get_token_value("py_pkg_dir")
        json_config["lo_identifier"] = token.get_token_value("lo_identifier")
        json_config["lo_implementation_name"] = token.get_token_value("lo_implementation_name")
        json_config["extension_display_name"] = token.get_token_value("display_name")
        json_config["oxt_name"] = token.get_token_value("oxt_name")
        json_config["lo_pip"] = token.get_token_value("lo_pip")
        json_config["libreoffice_debug_port"] = token.get_unprocessed_token_value("libreoffice_debug_port", 0)

        json_config["zipped_preinstall_pure"] = self._zip_preinstall_pure
        json_config["auto_install_in_site_packages"] = self._auto_install_in_site_packages
        json_config["install_wheel"] = self._install_wheel
        json_config["window_timeout"] = self._window_timeout
        json_config["dialog_desktop_owned"] = self._dialog_desktop_owned
        json_config["default_locale"] = self._default_locale
        json_config["resource_dir_name"] = self._resource_dir_name
        json_config["resource_properties_prefix"] = self._resource_properties_prefix
        json_config["isolate_windows"] = self._isolate_windows
        json_config["sym_link_cpython"] = self._sym_link_cpython
        json_config["uninstall_on_update"] = self._uninstall_on_update
        json_config["install_on_no_uninstall_permission"] = self._install_on_no_uninstall_permission
        json_config["unload_after_install"] = self._unload_after_install
        json_config["run_imports"] = self._run_imports
        json_config["run_imports2"] = self._run_imports2
        json_config["run_imports_linux"] = self._run_imports_linux
        json_config["run_imports_macos"] = self._run_imports_macos
        json_config["run_imports_win"] = self._run_imports_win
        # json_config["log_pip_installs"] = self._log_pip_installs
        json_config["log_indent"] = self._log_indent
        # update the requirements
        json_config["requirements"] = self._requirements

        json_config["has_locals"] = self._config.has_locals
        json_config["lp_debug_port"] = self._lp_debug_port
        json_config["require_install_name_match"] = self._require_install_name_match
        json_config["cmd_clean_file_prefix"] = self._cmd_clean_file_prefix

        # region tool.libre_pythonista.config
        json_config["cell_cp_prefix"] = self._cell_custom_prop_prefix
        json_config["cell_cp_codename"] = f"{self._cell_custom_prop_prefix}{self._cell_custom_prop_codename}"
        json_config["general_code_name"] = self._general_codename
        json_config["calc_props_json_name"] = self._calc_props_json_name
        json_config["lp_code_dir"] = self._lp_code_dir
        json_config["lp_default_log_format"] = self._lp_default_log_format
        json_config["extension_version"] = self._extension_version
        json_config["extension_license"] = self._extension_license
        json_config["author_names"] = self._author_names
        json_config["macro_lp_sheet_ctl_click"] = self._macro_lp_sheet_ctl_click
        json_config["macro_sheet_on_calculate"] = self._macro_sheet_on_calculate
        json_config["py_script_sheet_ctl_click"] = self._py_script_sheet_ctl_click
        json_config["py_script_sheet_on_calculate"] = self._py_script_sheet_on_calculate
        json_config["no_pip_remove"] = self._no_pip_remove
        json_config["pip_shared_dirs"] = self._pip_shared_dirs

        json_config["flatpak_libre_pythonista_py_editor"] = self._flatpak_libre_pythonista_py_editor
        json_config["flatpak_libre_pythonista_py_editor_cell_cmd"] = self._flatpak_libre_pythonista_py_editor_cell_cmd
        json_config["flatpak_libre_pythonista_py_editor_install_url"] = (
            self._flatpak_libre_pythonista_py_editor_install_url
        )

        json_config["lp_py_cell_edit_sock_timeout"] = self._lp_py_cell_edit_sock_timeout
        # endregion tool.libre_pythonista.config

        # region Requirements Rule
        json_config["py_packages"] = self._py_packages
        json_config["lp_editor_py_packages"] = self._lp_editor_py_packages
        # endregion Requirements Rule

        self._validate_config_dict(json_config)

        # save the file
        with open(json_config_path, "w", encoding="utf-8") as f:
            json.dump(json_config, f, indent=4)

    def _validate_config_dict(self, config_dict: Dict[str, str]) -> None:
        value = config_dict["py_pkg_dir"]
        assert isinstance(value, str), "py_pkg_dir must be an int"
        assert len(value) > 0, "py_pkg_dir must not be an empty string"
        assert not has_whitespace(value), "py_pkg_dir must not contain whitespace"

        value = config_dict["lo_identifier"]
        assert isinstance(value, str), "lo_identifier must be an int"
        assert len(value) > 0, "lo_identifier must not be an empty string"
        assert not has_whitespace(value), "lo_identifier must not contain whitespace"

        value = config_dict["lo_implementation_name"]
        assert isinstance(value, str), "lo_implementation_name must be an int"
        assert len(value) > 0, "lo_implementation_name must not be an empty string"
        assert not has_whitespace(value), "lo_implementation_name must not contain whitespace"

        value = config_dict["oxt_name"]
        assert isinstance(value, str), "oxt_name must be an int"
        assert len(value) > 0, "oxt_name must not be an empty string"

        value = config_dict["lo_pip"]
        assert isinstance(value, str), "lo_pip must be an int"
        assert len(value) > 0, "lo_pip must not be an empty string"
        assert not has_whitespace(value), "lo_pip must not contain whitespace"

        value = config_dict["libreoffice_debug_port"]
        assert isinstance(value, int), "libreoffice_debug_port must be an int"

    def _validate(self) -> None:
        """Validate"""
        assert isinstance(self._requirements, dict), "requirements must be a dict"
        assert isinstance(self._run_imports_linux, list), "run_imports_linux must be a list"
        assert isinstance(self._run_imports_macos, list), "run_imports_macos must be a list"
        assert isinstance(self._run_imports_win, list), "run_imports_win must be a list"

        assert isinstance(self._zip_preinstall_pure, bool), "zip_preinstall_pure must be a bool"
        assert isinstance(self._auto_install_in_site_packages, bool), "auto_install_in_site_packages must be a bool"
        assert isinstance(self._install_wheel, bool), "install_wheel must be a bool"
        assert isinstance(self._window_timeout, int), "window_timeout must be an int"
        assert isinstance(self._dialog_desktop_owned, bool), "dialog_desktop_owned must be a bool"
        assert isinstance(self._default_locale, list), "default_locale must be a list"
        assert len(self._default_locale) > 0, "default_locale must have at least 1 elements"
        assert len(self._default_locale) < 4, "default_locale must have no more then three elements"
        assert isinstance(self._resource_dir_name, str), "resource_dir_name must be a string"
        assert len(self._resource_dir_name) > 0, "resource_dir_name must not be an empty string"
        assert isinstance(self._resource_properties_prefix, str), "resource_properties_prefix must be a string"
        assert len(self._resource_properties_prefix) > 0, "resource_properties_prefix must not be an empty string"
        assert isinstance(self._sym_link_cpython, bool), "sym_link_cpython must be a bool"
        assert isinstance(self._uninstall_on_update, bool), "uninstall_on_update must be a bool"
        assert isinstance(self._unload_after_install, bool), "unload_after_install must be a bool"
        assert isinstance(self._log_indent, int), "log_indent must be a int"
        assert isinstance(self._install_on_no_uninstall_permission, bool), (
            "_install_on_no_uninstall_permission must be a bool"
        )
        assert isinstance(self._run_imports, list), "run_imports must be a list"
        assert isinstance(self._run_imports2, list), "run_imports2 must be a list"
        assert isinstance(self._lp_debug_port, int), "lp_debug_port must be a int"
        assert isinstance(self._require_install_name_match, bool), "require_install_name_match must be a bool"
        # region tool.libre_pythonista.config
        assert isinstance(self._cell_custom_prop_prefix, str), "cell_custom_prop_prefix must be a string"
        assert isinstance(self._cell_custom_prop_codename, str), "cell_custom_prop_codename must be a string"
        assert isinstance(self._general_codename, str), "general_codename must be a string"
        assert isinstance(self._calc_props_json_name, str), "calc_props_json_name must be a string"
        assert isinstance(self._lp_code_dir, str), "lp_code_dir must be a string"
        assert isinstance(self._lp_default_log_format, str), "log format must be a string"
        assert self._lp_default_log_format, "lp_default_log_format must not be an empty string"
        assert isinstance(self._cmd_clean_file_prefix, str), "cmd_clean_file_prefix must be a string"
        assert len(self._cmd_clean_file_prefix) > 0, "cmd_clean_file_prefix must not be an empty string"
        assert isinstance(self._pip_shared_dirs, list), "pip_shared_dirs must be a list"
        for pip_dir in self._pip_shared_dirs:
            assert isinstance(pip_dir, str), "pip_shared_dirs must be a list of strings"
            assert len(pip_dir) > 0, "pip_shared_dirs must not be an empty string"
            assert not has_whitespace(pip_dir), "pip_shared_dirs must not contain whitespace"

        # validate the extension version is a valid python version
        assert self._extension_version.count(".") == 2, "extension_version must contain two periods"
        assert isinstance(self._no_pip_remove, list), "no_pip_remove must be a list"

        assert isinstance(self._flatpak_libre_pythonista_py_editor, str), (
            "flatpak_libre_pythonista_py_editor must be a string"
        )
        assert isinstance(self._flatpak_libre_pythonista_py_editor_cell_cmd, str), (
            "flatpak_libre_pythonista_py_editor_cell_cmd must be a string"
        )
        # endregion tool.libre_pythonista.config

    def _warnings(self) -> None:
        warnings = []
        token = Token()
        dist_dir = cast(str, self._cfg["tool"]["oxt"]["config"]["dist_dir"])
        log_level = str(token.get_token_value("log_level"))
        log_format = str(token.get_token_value("log_format"))
        lp_experimental_editor = str(token.get_token_value("lp_experimental_editor"))

        if self._log_indent > 0:
            warnings.append(f"'tool.oxt.config.log_indent' is set to {self._log_indent}. Set to 0 for production.")
        if dist_dir == "tmp_dist":
            warnings.append("'tool.oxt.config.dist_dir' is set to the default value of 'tmp_dist'.")
        if log_level != "INFO":
            warnings.append(f"'tool.oxt.config.log_level' is set to '{log_level}'. Set to INFO for production.")
        if "indent_str" in log_format:
            warnings.append(
                "'tool.oxt.config.log_format' contains 'indent_str'. This is for debugging. Remove for production."
            )
        if lp_experimental_editor != "false":
            warnings.append(
                f"'lp_experimental_editor' is set to '{lp_experimental_editor}'. This is for development. Set to 'false' for production."
            )
        if self._lp_py_cell_edit_sock_timeout > 10:
            warnings.append(
                f"'lp_py_cell_edit_sock_timeout' is set to '{self._lp_py_cell_edit_sock_timeout}'. Set to 10 for production."
            )
        if warnings:
            print("JsonConfig Warnings:")
            for warning in warnings:
                print(f"  {warning}")
            print()
