from __future__ import annotations
from typing import Any, TYPE_CHECKING
import logging

try:
    # python 3.10+
    from typing import TypeGuard  # type: ignore
except ImportError:
    from typing_extensions import TypeGuard

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override


from ooodev.calc import CalcDoc

from .custom_props_base import CustomPropsBase
from ..state.calc_state_mgr import CalcStateMgr


if TYPE_CHECKING:
    from ....___lo_pip___.config import Config
    from ooodev.proto.office_document_t import OfficeDocumentT
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

        cfg = Config()
        if self._is_calc_doc(doc):
            self._state_mgr = CalcStateMgr(doc)
        else:
            raise ValueError("Invalid document type. Document must be a Calc document.")
        file_name = f"{cfg.general_code_name}_calc_props.json"
        CustomPropsBase.__init__(self, doc=doc, file_name=file_name, props_id="calc_custom_props")
        if self._log.is_debug:
            with self._log.indent(True):
                self._log.debug(f"Setting log_level: {self.log_level}")
                self._log.debug(f"Setting log_format: {self.log_format}")
                self._log.debug(f"Setting log_to_console: {self.log_to_console}")
                self._log.debug(f"Setting include_extra_err_info: {self.include_extra_err_info}")
        # please the type checker

    def _is_calc_doc(self, doc: Any) -> TypeGuard[CalcDoc]:
        return isinstance(doc, CalcDoc)

    @override
    def _is_doc_props_ready(self) -> bool:
        """
        Checks if the document properties are ready.

        Returns:
            bool: ``True`` if the document properties are ready, otherwise ``False``.
        """
        return self._state_mgr.is_pythonista_doc

    def update_doc_ext_location(self) -> None:
        """
        Update the document extension location from the config.
        """
        self.doc_ext_location = "user" if self.config.is_user_installed else "share"

    # region Properties
    @property
    def doc_ext_location(self) -> str:
        """Gets/sets the document extension location. Must be ``share`` or ``user``."""
        if self.config.is_shared_installed:
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
        return self.get_custom_property("log_format", self.config.lp_default_log_format)

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

    @property
    @override
    def doc(self) -> CalcDoc:
        """Calc Document"""
        return super().doc  # type: ignore

    # endregion Properties
