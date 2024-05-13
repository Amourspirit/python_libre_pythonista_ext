from __future__ import annotations
from typing import cast, Any, Dict, List
import toml
from ..meta.singleton import Singleton
from .. import file_util


class Token(metaclass=Singleton):
    """Singleton Class the tokens."""

    def __init__(self) -> None:
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        cfg = toml.load(toml_path)

        tokens = cast(Dict[str, str], cfg["tool"]["oxt"]["token"])
        self._validate_toml_dict(tokens)
        self._tokens: Dict[str, str] = {}
        for token, replacement in tokens.items():
            self._tokens[f"___{token}___"] = replacement
        self._tokens["___version___"] = str(cfg["tool"]["poetry"]["version"])
        self._tokens["___license___"] = str(cfg["tool"]["poetry"]["license"])
        self._tokens["___oxt_name___"] = str(cfg["tool"]["oxt"]["config"]["oxt_name"])
        self._tokens["___dist_dir___"] = str(cfg["tool"]["oxt"]["config"]["dist_dir"])
        self._tokens["___update_file___"] = str(cfg["tool"]["oxt"]["config"]["update_file"])
        self._tokens["___py_pkg_dir___"] = str(cfg["tool"]["oxt"]["config"]["py_pkg_dir"])
        authors = self._get_authors(cfg)
        self._tokens["___authors___"] = ", ".join(authors)
        self._tokens["___contributors___"] = "\n".join(authors)
        for token, replacement in self._tokens.items():
            self._tokens[token] = self.process(replacement)
        self._tokens_remove_whitespace()

    # region Methods
    def _validate_toml_dict(self, cfg: Dict[str, Any]) -> None:
        # sourcery skip: extract-method
        key_types = {
            "lo_identifier": str,
            "lo_implementation_name": str,
            "publisher": str,
            "display_name": str,
            "description": str,
            "url_pip": str,
            "log_format": str,
            "lo_pip": str,
            "platform": str,
            "startup_event": str,
            "log_level": str,
            "show_progress": bool,
            "delay_startup": bool,
            "log_pip_installs": bool,
            "log_add_console": bool,
        }
        for key, value in key_types.items():
            if key not in cfg:
                raise ValueError(f"Key '{key}' not found")
            if not isinstance(cfg[key], value):
                raise ValueError(f"Key '{key}' must be {value.__name__}, got: {type(cfg[key]).__name__}")
            if value is str and not cfg[key]:
                raise ValueError(f"Key '{key}' is empty")

        allow_empty_key_types = {
            "pip_wheel_url": str,
            "test_internet_url": str,
        }
        for key, value in allow_empty_key_types.items():
            if key not in cfg:
                raise ValueError(f"Key '{key}' not found")
            if not isinstance(cfg[key], value):
                raise ValueError(f"Key '{key}' must be {value.__name__}, got: {type(cfg[key]).__name__}")

        levels = {"none", "debug", "info", "warning", "error", "critical"}
        value = str(cfg.get("log_level", "")).lower()
        if value not in levels:
            raise ValueError(f"Token 'log_level' is invalid: {value}")

        lo_identifier = str(cfg.get("lo_identifier", ""))
        if lo_identifier != "org.openoffice.extensions.ooopip":
            value = str(cfg.get("lo_implementation_name", ""))
            if value == "OooPipRunner":
                raise ValueError(
                    "Token 'lo_implementation_name' value is invalid and must be renamed in tool.oxt.token in pyproject.toml. Every project must have unique lo_implementation_name value."
                )

            value = str(cfg.get("lo_pip", ""))
            if value == "lo_pip":
                raise ValueError(
                    "Token 'lo_pip' value is invalid and must be renamed in tool.oxt.token in pyproject.toml. Every project must have unique lo_pip value."
                )
            value = str(cfg.get("log_file", ""))
            if value == "pip_install.log":
                raise ValueError(
                    "Token 'log_file' value is invalid and must be renamed in tool.oxt.token in pyproject.toml. Every project must have unique log_file value or set to empty string for no logging."
                )

        value = str(cfg.get("startup_event", ""))
        if value not in {"onFirstVisibleTask", "OnStartApp"}:
            raise ValueError(
                f"Token 'startup_event' value is invalid: {value}. Valid values are: '', 'onFirstVisibleTask', 'OnStartApp'."
            )
        # show_progress

    def _tokens_remove_whitespace(self) -> None:
        """Cleans the tokens."""

        def remove_spaces(text: str) -> str:
            return text.replace(" ", "")

        keys = {
            "lo_identifier",
            "url_pip",
            "platform",
        }
        for key in keys:
            str_key = f"___{key}___"
            if str_key in self._tokens:
                self._tokens[str_key] = remove_spaces(self._tokens[str_key])

    def process(self, value: Any) -> str:
        """Processes the given text."""
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)):
            return str(value)
        if not isinstance(value, str):
            return str(value)
        for token, replacement in self._tokens.items():
            value = value.replace(token, str(replacement))

        return value

    def get_token_value(self, token: str) -> Any:
        """
        Returns the value of the given token.

        Args:
            token (str): The token in normal form (without '___' at the beginning and end).
        """
        return self._tokens.get(f"___{token}___", "")

    def _get_authors(self, cfg: Dict[str, Any]) -> List[str]:
        """Returns the authors."""
        authors = cast(List[str], cfg["tool"]["poetry"]["authors"])
        results: List[str] = [author.split("<")[0].strip() for author in authors]
        return results

    # endregion Methods

    # region Properties
    @property
    def tokens(self) -> Dict[str, str]:
        """The tokens."""
        return self._tokens

    # endregion Properties
