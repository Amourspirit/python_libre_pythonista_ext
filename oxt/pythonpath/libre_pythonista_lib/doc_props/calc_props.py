from __future__ import annotations
from typing import Any, TYPE_CHECKING
import logging


try:
    # python 3.10+
    from typing import TypeGuard  # type: ignore
except ImportError:
    from typing_extensions import TypeGuard


from ooodev.calc import CalcDoc

from .custom_props_base import CustomPropsBase

# from ..state.calc_state_mgr import CalcStateMgr


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ooodev.utils.helper.dot_dict import DotDict
    from ..doc.calc_doc_mgr import CalcDocMgr
    from ....___lo_pip___.config import Config
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.utils.custom_ext import override


class CalcProps(CustomPropsBase):
    """
    Class to add custom properties to a Calc document for LibrePythonista. The properties are stored in a json file embedded in the document.
    """

    def __init__(self, doc: OfficeDocumentT) -> None:
        """
        Constructor.

        Args:
            doc (Any): The document.
        """
        self._calc_props_log = None
        cfg = Config()
        # if self._is_calc_doc(doc):
        #     self._state_mgr = CalcStateMgr(doc)
        # else:
        #     raise ValueError("Invalid document type. Document must be a Calc document.")
        # file_name = f"{cfg.general_code_name}_calc_props.json"
        file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"

        self._is_imported_calc_doc_mgr = False
        CustomPropsBase.__init__(self, doc=doc, file_name=file_name, props_id="calc_custom_props")

        self._doc_mgr: CalcDocMgr
        if self.log.is_debug:
            with self.log.indent(True):
                self.log.debug("Setting log_level: %i", self.log_level)
                self.log.debug("Setting log_format: %s", self.log_format)
                self.log.debug("Setting log_to_console: %s", self.log_to_console)
                self.log.debug("Setting include_extra_err_info: %s", self.include_extra_err_info)
        # please the type checker

    def _ensure_import_calc_doc_mgr(self) -> None:
        """
        Ensures that the CalcDocMgr module is imported and initializes the CalcDocMgr instance.
        This method checks if the CalcDocMgr module has already been imported. If not, it attempts to import the module
        from the relative path and initializes an instance of CalcDocMgr. If the import fails, it logs the exception
        and raises an ImportError.
        Raises:
            ImportError: If the CalcDocMgr module cannot be imported.
        """

        if self._is_imported_calc_doc_mgr:
            return

        try:
            from ..doc.calc_doc_mgr import CalcDocMgr
        except ImportError:
            self.log.exception("ImportError: CalcDocMgr")
            raise
        self._doc_mgr = CalcDocMgr()
        self._is_imported_calc_doc_mgr = True

    def _ensure_doc_json_file(self) -> None:
        """
        Ensures that the document json file exists.
        """
        self._ensure_import_calc_doc_mgr()
        if self._doc_mgr.events_ensured:
            self.is_doc_props = True
            super()._ensure_doc_json_file()
        else:
            self.log.debug("_ensure_doc_json_file() Events not ensured. Document json file not ensured.")

    # region Overrides
    @override
    def _get_log(self) -> OxtLogger:
        """
        Gets the logger.

        Returns:
            OxtLogger: The logger.
        """
        if self._calc_props_log is None:
            self._calc_props_log = OxtLogger(log_name=self.__class__.__name__)
        return self._calc_props_log

    @override
    def _is_doc_props_ready(self) -> bool:
        """
        Checks if the document properties are ready.

        Returns:
            bool: ``True`` if the document properties are ready, otherwise ``False``.
        """
        # return self._state_mgr.is_pythonista_doc
        return self.is_doc_props

    @override
    def _init_props(self) -> None:
        """
        Initializes the properties.
        """
        self._ensure_import_calc_doc_mgr()
        if self._doc_mgr.events_ensured:
            super()._init_props()
        else:
            self.log.debug("_init_props() Events not ensured. Properties not initialized.")

    @override
    def set_custom_property(self, name: str, value: Any) -> None:  # noqa: ANN401
        """
        Sets a custom property.

        Args:
            name (str): The name of the property.
            value (Any): The value of the property.

        Raises:
            AttributeError: If the property is a forbidden key.
        """
        self._ensure_import_calc_doc_mgr()
        if self._doc_mgr.events_ensured:
            super().set_custom_property(name, value)
        else:
            self.log.debug("set_custom_property() Events not ensured. Property not set.")

    @override
    def set_custom_properties(self, properties: DotDict) -> None:
        """
        Sets custom properties.

        Args:
            properties (DotDict): custom properties to set.

        Hint:
            DotDict is a class that allows you to access dictionary keys as attributes or keys.
            DotDict can be imported from ``ooodev.utils.helper.dot_dict.DotDict``.
        """
        self._ensure_import_calc_doc_mgr()
        if self._doc_mgr.events_ensured:
            super().set_custom_properties(properties)
        else:
            self.log.debug("set_custom_properties() Events not ensured. Properties not set.")

    # endregion Overrides

    def _is_calc_doc(self, doc: Any) -> TypeGuard[CalcDoc]:  # noqa: ANN401
        return isinstance(doc, CalcDoc)

    def update_doc_ext_location(self) -> None:
        """
        Update the document extension location from the config.
        """
        self.doc_ext_location = "user" if self.config.is_user_installed else "share"

    # region Properties
    @property
    def doc_ext_location(self) -> str:
        """Gets/sets the document extension location. Must be ``share`` or ``user``."""
        if self.config.is_shared_installed:  # noqa: SIM108
            location = "share"
        else:
            location = "user"
        return self.get_custom_property("doc_ext_location", location)

    @doc_ext_location.setter
    def doc_ext_location(self, value: str) -> None:
        if value not in ("share", "user"):
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
