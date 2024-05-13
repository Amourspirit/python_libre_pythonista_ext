from __future__ import annotations
from typing import Dict, cast, NamedTuple, List, TypedDict
from pathlib import Path
import toml
from lxml import etree
from ... import file_util
from ...config import Config
from ..token import Token


class Element(NamedTuple):
    """Element of the description file."""

    href: str
    lang: str
    text: str


class PublisherT(TypedDict):
    """Publisher locale."""

    name: str
    url: str


class Publisher:
    """Reads Locale descriptions from pyproject.toml and writes them to description.xml."""

    def __init__(self) -> None:
        self._token = Token()
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        cfg = toml.load(toml_path)

        self._locales = cast(Dict[str, PublisherT], cfg["tool"]["oxt"]["locale"]["publisher"])

        self._config = Config()
        self._descriptions_path = self._config.build_path / "pkg-desc"
        self._xml_desc_path = self._get_xml_path()

    def write(self) -> None:
        """Create the description file for the locales."""
        elements: List[Element] = []

        for key, value in self._locales.items():
            if not value:
                continue

            lang = key.replace("_", "-")
            name = self._token.process(value["name"])
            url = self._token.process(value["url"])
            elements.append(Element(href=url, lang=lang, text=name))
        self._write_xml(elements, self._xml_desc_path)

    def _get_xml_path(self) -> Path:
        return self._config.build_path / "description.xml"

    def _write_xml(self, elements: List[Element], xml_path: Path) -> None:
        """Write the description.xml file."""
        if not elements:
            return
        xml_file = etree.parse(xml_path, etree.XMLParser(remove_blank_text=True))
        root = xml_file.getroot()

        publishers = root.find("{http://openoffice.org/extensions/description/2006}publisher")
        if publishers is None:
            publishers = etree.Element("publisher", attrib=None, nsmap=None)
            root.append(publishers)

        for element in elements:
            publisher = etree.Element("name", attrib=None, nsmap=root.nsmap)
            publisher.set("{http://www.w3.org/1999/xlink}href", element.href)
            publisher.set("lang", element.lang)
            publisher.text = element.text
            publishers.append(publisher)

        xml_file.write(xml_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
