from __future__ import annotations
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from ___lo_pip___.basic_config import BasicConfig


class CalcProps2:
    """
    Class to add custom properties to a Calc document for LibrePythonista. The properties are stored in a json file embedded in the document.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._cfg = BasicConfig()
        self._log_level = logging.INFO
        self._log_format = self._cfg.lp_default_log_format
        self._log_to_console = False
        self._include_extra_err_info = False

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
        props._log_level = data.get("log_level", logging.INFO)
        props._log_format = data.get("log_format", props._cfg.lp_default_log_format)
        props._log_to_console = data.get("log_to_console", False)
        props._include_extra_err_info = data.get("include_extra_err_info", False)
        return props

    # region Properties
    @property
    def log_level(self) -> int:
        return self._log_level

    @log_level.setter
    def log_level(self, value: int) -> None:
        self._log_level = value

    @property
    def log_format(self) -> str:
        return self._log_format

    @log_format.setter
    def log_format(self, value: str) -> None:
        self._log_format = value

    @property
    def log_to_console(self) -> bool:
        return self._log_to_console

    @log_to_console.setter
    def log_to_console(self, value: bool) -> None:
        self._log_to_console = value

    @property
    def include_extra_err_info(self) -> bool:
        return self._include_extra_err_info

    @include_extra_err_info.setter
    def include_extra_err_info(self, value: bool) -> None:
        self._include_extra_err_info = value

    # endregion Properties
