from __future__ import annotations
from typing import Dict, cast, List
import toml
from lxml import etree
from ... import file_util
from ...config import Config
from ..token import Token


class Name:
    """Reads Locale names from pyproject.toml and writes them to description.xml."""

    def __init__(self) -> None:
        self._token = Token()
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        cfg = toml.load(toml_path)

        self._locales = cast(Dict[str, str], cfg["tool"]["oxt"]["locale"]["name"])

        self._config = Config()
        self._descriptions_path = self._config.build_path / "pkg-desc"
        self._xml_path = self._config.build_path / "description.xml"

    def write(self) -> None:
        """Create the description file for the locales."""
        elements: Dict[str, str] = {}

        for key, value in self._locales.items():
            if not value:
                continue
            lang = key.replace("_", "-")
            elements[lang] = self._token.process(value)
        self._write_xml(elements)

    def _write_xml(self, elements: Dict[str, str]) -> None:
        """Write the description.xml file."""
        if not elements:
            return
        xml_file = etree.parse(self._xml_path, etree.XMLParser(remove_blank_text=True))
        root = xml_file.getroot()

        names = root.find("{http://openoffice.org/extensions/description/2006}display-name")
        if names is None:
            names = etree.Element("display-name", attrib=None, nsmap=None)
            root.append(names)

        for key, value in elements.items():
            desc = etree.Element("name", attrib=None, nsmap=None)
            desc.set("lang", key)
            desc.text = value
            names.append(desc)

        xml_file.write(self._xml_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
