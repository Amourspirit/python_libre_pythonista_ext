from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from .custom_props_base import CustomPropsBase


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class CalcProps(CustomPropsBase):
    """
    Class to add custom properties to a Calc document for LibrePythonista. The properties are stored in a json file embedded in the document.
    """

    def __init__(self, doc: OfficeDocumentT):
        """
        Constructor.

        Args:
            doc (Any): The document.
        """
        if getattr(self, "_is_init", False):
            return

        cfg = Config()
        file_name = f"{cfg.general_code_name}_calc_props.json"
        CustomPropsBase.__init__(self, doc=doc, file_name=file_name, props_id="calc_custom_props")
        if self._log.is_debug:
            with self._log.indent(True):
                self._log.debug(f"Setting log_level: {self.log_level}")
                self._log.debug(f"Setting log_format: {self.log_format}")
                self._log.debug(f"Setting log_to_console: {self.log_to_console}")
                self._log.debug(f"Setting include_extra_err_info: {self.include_extra_err_info}")
        self._is_init = True
        # please the type checker

    def update_doc_ext_location(self) -> None:
        """
        Update the document extension location from the config.
        """
        self.doc_ext_location = "user" if self._cfg.is_user_installed else "share"

    # region Properties
    @property
    def doc_ext_location(self) -> str:
        """Gets/sets the document extension location. Must be ``share`` or ``user``."""
        if self._cfg.is_shared_installed:
            location = "share"
        else:
            location = "user"
        return self.get_custom_property("doc_ext_location", location)

    @doc_ext_location.setter
    def doc_ext_location(self, value: str) -> None:
        if not value in ("share", "user"):
            raise ValueError(f"Invalid value for doc_ext_location: {value}")
        self.set_custom_property("doc_ext_location", value)

    @property
    def log_level(self) -> int:
        return self.get_custom_property("log_level", logging.INFO)

    @log_level.setter
    def log_level(self, value: int) -> None:
        self.set_custom_property("log_level", value)

    @property
    def log_format(self) -> str:
        return self.get_custom_property("log_format", self._cfg.lp_default_log_format)

    @log_format.setter
    def log_format(self, value: str) -> None:
        self.set_custom_property("log_format", value)

    @property
    def log_to_console(self) -> bool:
        return self.get_custom_property("log_to_console", False)

    @log_to_console.setter
    def log_to_console(self, value: bool) -> None:
        self.set_custom_property("log_to_console", value)

    @property
    def include_extra_err_info(self) -> bool:
        return self.get_custom_property("include_extra_err_info", False)

    @include_extra_err_info.setter
    def include_extra_err_info(self, value: bool) -> None:
        self.set_custom_property("include_extra_err_info", value)

    # endregion Properties
