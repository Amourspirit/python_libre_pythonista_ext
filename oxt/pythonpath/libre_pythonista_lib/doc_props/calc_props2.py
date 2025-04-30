from __future__ import annotations
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from oxt.___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_doc_prop.py


class CalcProps2:
    """
    Class to add custom properties to a Calc document for LibrePythonista. The properties are stored in a json file embedded in the document.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._cfg = self._get_config()
        self._log_level = logging.INFO
        self._log_format = self._cfg.lp_default_log_format
        self._log_to_console = False
        self._include_extra_err_info = False
        self._is_modified = False
        self._doc_ext_location = "user" if self._cfg.is_user_installed else "share"

    def _get_config(self) -> Config:
        # for testing
        return Config()

    def __copy__(self) -> CalcProps2:
        """
        Creates a copy of the CalcProps2 instance.

        Returns:
            CalcProps2: The copy of the CalcProps2 instance.
        """
        inst = CalcProps2()
        inst._log_level = self._log_level
        inst._log_format = self._log_format
        inst._log_to_console = self._log_to_console
        inst._include_extra_err_info = self._include_extra_err_info
        inst._is_modified = self._is_modified
        inst._doc_ext_location = self._doc_ext_location
        return inst

    def to_dict(self) -> dict:
        """
        Converts the CalcProps2 instance to a dictionary.

        Returns:
            dict: The dictionary representation of the CalcProps2 instance.
        """
        return {
            "log_level": self._log_level,
            "log_format": self._log_format,
            "log_to_console": self._log_to_console,
            "include_extra_err_info": self._include_extra_err_info,
            "doc_ext_location": self._doc_ext_location,
        }

    def copy(self) -> CalcProps2:
        """
        Creates a copy of the CalcProps2 instance.

        Returns:
            CalcProps2: The copy of the CalcProps2 instance.
        """
        return self.__copy__()

    @staticmethod
    def from_dict(data: dict) -> CalcProps2:
        """
        Creates a CalcProps2 instance from a dictionary.

        Args:
            data (dict): The dictionary to create the CalcProps2 instance from.

        Returns:
            CalcProps2: The CalcProps2 instance.
        """
        props = CalcProps2()
        props._log_level = data.get("log_level", props._log_level)
        props._log_format = data.get("log_format", props._log_format)
        props._log_to_console = data.get("log_to_console", props._log_to_console)
        props._include_extra_err_info = data.get("include_extra_err_info", props._include_extra_err_info)
        props._doc_ext_location = data.get("doc_ext_location", props._doc_ext_location)
        props._is_modified = False
        return props

    def _mark_modified(self) -> None:
        """Marks the properties as modified."""
        self._is_modified = True

    def reset_modified(self) -> None:
        """Resets the modified state."""
        self._is_modified = False

    # region Properties
    @property
    def is_modified(self) -> bool:
        """Returns whether any properties have been modified since initialization or last reset."""
        return self._is_modified

    @property
    def log_level(self) -> int:
        return self._log_level

    @log_level.setter
    def log_level(self, value: int) -> None:
        if self._log_level != value:
            self._log_level = value
            self._mark_modified()

    @property
    def log_format(self) -> str:
        return self._log_format

    @log_format.setter
    def log_format(self, value: str) -> None:
        if self._log_format != value:
            self._log_format = value
            self._mark_modified()

    @property
    def log_to_console(self) -> bool:
        return self._log_to_console

    @log_to_console.setter
    def log_to_console(self, value: bool) -> None:
        if self._log_to_console != value:
            self._log_to_console = value
            self._mark_modified()

    @property
    def include_extra_err_info(self) -> bool:
        return self._include_extra_err_info

    @include_extra_err_info.setter
    def include_extra_err_info(self, value: bool) -> None:
        if self._include_extra_err_info != value:
            self._include_extra_err_info = value
            self._mark_modified()

    @property
    def doc_ext_location(self) -> str:
        return self._doc_ext_location

    @doc_ext_location.setter
    def doc_ext_location(self, value: str) -> None:
        if self._doc_ext_location != value:
            self._doc_ext_location = value
            self._mark_modified()

    # endregion Properties
