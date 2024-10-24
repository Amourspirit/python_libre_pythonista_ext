from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib
from abc import abstractmethod
from ooodev.utils.gen_util import NULL_OBJ
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.io.json.doc_json_file import DocJsonFile


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT

    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


class CustomPropsBase:
    """
    Class to add custom properties to a document. The properties are stored in a json file embedded in the document.

    Allows custom properties to be added to a document.

    Note:
        Any value that can be serialized to JSON can be stored as a custom property.
        Classes can implement the :py:class:`ooodev.io.json.json_encoder.JsonEncoder` class to provide custom serialization by overriding the ``on_json_encode()`` method.
    """

    def __init__(self, doc: OfficeDocumentT, file_name: str, props_id: str):
        """
        Constructor.

        Args:
            doc (Any): The document.
            file_name (str, optional): The name of the file to store the properties. Defaults to "DocumentCustomProperties.json".
        """
        self._is_props_init = False
        self._is_doc_props_flag = False
        self._cfg = Config()
        with self.log.indent(True):
            self.log.debug("Init")
        self._doc = doc
        self._json_doc = None
        self._props_id = props_id
        if not file_name.endswith(".json"):
            file_name = f"{file_name}.json"
        self._name = file_name
        self._file_exist = False
        self._props = {}
        with self.log.indent(True):
            self.log.debug(f"File Name: {self._name}")
            self.log.debug("End Init")
        # please the type checker

    def _init_props(self):
        """
        Initializes the properties.
        """
        if self._is_props_init:
            self.log.debug("_init_props() Properties Already Initialized")
            return
        self._props = self._get_custom_properties()
        # self._ensure_doc_json_file()
        self._is_props_init = True
        self.log.debug("_init_props() Properties Initialized")

    @abstractmethod
    def _get_log(self) -> OxtLogger:
        """
        Gets the logger.

        Returns:
            OxtLogger: The logger.
        """
        raise NotImplementedError

    @abstractmethod
    def _is_doc_props_ready(self) -> bool:
        """
        Checks if the document properties are ready.

        Returns:
            bool: ``True`` if the document properties are ready, otherwise ``False``.
        """
        raise NotImplementedError

    def _ensure_doc_json_file(self) -> None:
        """
        Ensures the document JSON file exists.
        """
        with self.log.indent(True):
            if self._is_doc_props_ready() is False:
                self.log.error("_ensure_doc_json_file() Document properties are not ready. Not Saving.")
                return
            try:
                if self._json_doc is None:
                    # the creation of DocJsonFile will create the file if it does not exist
                    self._json_doc = DocJsonFile(self._doc, "json")
                    if not self._json_doc.file_exist(self._name):
                        # set an empty dictionary as the data
                        self._json_doc.write_json(self._name, {})
                    self.log.debug(f"_ensure_doc_json_file() JSON File Created: {self._name}")
            except Exception:
                self.log.error(f"_ensure_doc_json_file() Error ensuring JSON file: {self._name}", exc_info=True)

    def _get_custom_properties(self) -> dict:
        """
        Loads custom properties from the hidden control.
        """
        with self.log.indent(True):
            # self._ensure_doc_json_file()
            if self._is_doc_props_ready() is False or self._json_doc is None:
                self.log.debug(
                    f"_get_custom_properties() File does not exist: {self._name}. Returning empty dictionary."
                )
                return {}
            try:
                result = self._json_doc.read_json(self._name)
                return result.get("data", {})
            except Exception:
                self.log.error(
                    f"_get_custom_properties() Error reading JSON file: {self._name}. Returning empty dictionary.",
                    exc_info=True,
                )
                return {}

    def _save_properties(self, data: dict) -> None:
        """
        Saves custom properties to the hidden control.

        Args:
            properties (dict): The properties to save.
        """
        self._init_props()
        with self.log.indent(True):
            self._ensure_doc_json_file()
            p_ready = self._is_doc_props_ready()
            if p_ready is False or self._json_doc is None:
                self.log.error("_save_properties() Document properties are not ready. Not Saving.")
                return
            try:
                json_data = {
                    "id": f"{self._cfg.lo_identifier}.{self._cfg.lo_implementation_name}.{self._props_id}",
                    "version": self._cfg.extension_version,
                    "data": data,
                }
                assert self._json_doc is not None
                self._json_doc.write_json(self._name, json_data)
            except Exception:
                self.log.error(f"_save_properties() Error writing JSON file: {self._name}", exc_info=True)

    def get_custom_property(self, name: str, default: Any = NULL_OBJ) -> Any:
        """
        Gets a custom property.

        Args:
            name (str): The name of the property.
            default (Any, optional): The default value to return if the property does not exist.

        Raises:
            AttributeError: If the property is not found.

        Returns:
            Any: The value of the property.
        """
        self._init_props()
        with self.log.indent(True):
            result = self._props.get(name, default)
            if result is NULL_OBJ:
                self.log.error(f"get_custom_property() Property '{name}' not found.")
                raise AttributeError(f"Property '{name}' not found.")
            return result

    def set_custom_property(self, name: str, value: Any):
        """
        Sets a custom property.

        Args:
            name (str): The name of the property.
            value (Any): The value of the property.

        Raises:
            AttributeError: If the property is a forbidden key.
        """
        self._init_props()
        with self.log.indent(True):
            try:
                props = self._props.copy()
                props[name] = value
                self._save_properties(props)
                self._props = props
                self.log.debug(f"Property '{name}' set.")
            except Exception:
                self.log.error(f"Error setting property '{name}'", exc_info=True)

    def get_custom_properties(self) -> DotDict:
        """
        Gets custom properties.

        Returns:
            DotDict: custom properties.

        Hint:
            DotDict is a class that allows you to access dictionary keys as attributes or keys.
            DotDict can be imported from ``ooodev.utils.helper.dot_dict.DotDict``.
        """
        self._init_props()
        dd = DotDict()
        dd.update(self._props)
        return dd

    def set_custom_properties(self, properties: DotDict) -> None:
        """
        Sets custom properties.

        Args:
            properties (DotDict): custom properties to set.

        Hint:
            DotDict is a class that allows you to access dictionary keys as attributes or keys.
            DotDict can be imported from ``ooodev.utils.helper.dot_dict.DotDict``.
        """
        self._init_props()
        with contextlib.suppress(Exception):
            props = self._props.copy()
            props.update(properties.copy_dict())
            self._save_properties(props)
            self._props = props

    def remove_custom_property(self, name: str) -> None:
        """
        Removes a custom property.

        Args:
            name (str): The name of the property to remove.

        Raises:
            AttributeError: If the property is a forbidden key.

        Returns:
            None:
        """
        self._init_props()
        with self.log.indent(True):
            try:
                props = self._props.copy()
                if name in props:
                    del props[name]
                    self._save_properties(props)
                    self._props = props
                    self.log.debug(f"Property '{name}' removed.")
            except Exception:
                self.log.error(f"Error removing property '{name}'", exc_info=True)

    def has_custom_property(self, name: str) -> bool:
        """
        Gets if a custom property exists.

        Args:
            name (str): The name of the property to check.

        Returns:
            bool: ``True`` if the property exists, otherwise ``False``.
        """
        self._init_props()
        return name in self._props

    # region Properties

    @property
    def log(self) -> OxtLogger:
        """Class Logger"""
        return self._get_log()

    @property
    def config(self) -> Config:
        """Config"""
        return self._cfg

    @property
    def doc(self) -> OfficeDocumentT:
        """Document"""
        return self._doc

    @property
    def is_doc_props(self) -> bool:
        """
        Gets/Sets if the document properties file exists in  the document.

        Returns:
            bool: ``True`` if the file exists, otherwise ``False``.
        """
        if self._is_doc_props_flag:
            self.log.debug("is_doc_props - JSON file exists. Returning True.")
            return True

        if self._json_doc is None:
            djf = DocJsonFile(self._doc, "json")
            if djf.file_exist(self._name):
                self._json_doc = djf
                self._is_doc_props_flag = True
                self.log.debug("is_doc_props - JSON file exists. Returning True.")
                return True
            with self.log.indent(True):
                self.log.error("is_doc_props - JSON file does not exist. Returning False.")
            return False
        else:
            self._file_exist = self._json_doc.file_exist(self._name)
            if self._file_exist:
                self._is_doc_props_flag = True
                self.log.debug("is_doc_props - JSON file exists. Returning True.")
                return True
            else:
                self._is_doc_props_flag = False
                with self.log.indent(True):
                    self.log.error("is_doc_props - JSON file does not exist. Returning False.")
                return False

    @is_doc_props.setter
    def is_doc_props(self, value: bool) -> None:
        self._is_doc_props_flag = value
        if value:
            if self._json_doc is None:
                self._json_doc = DocJsonFile(self._doc, "json")
        else:
            self._json_doc = None

    # endregion Properties
