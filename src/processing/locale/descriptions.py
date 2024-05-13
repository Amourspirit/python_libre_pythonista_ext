from __future__ import annotations
from typing import Dict, cast, NamedTuple, List
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


class Descriptions:
    """Reads Locale descriptions from pyproject.toml and writes them to description.xml."""

    def __init__(self) -> None:
        self._token = Token()
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        cfg = toml.load(toml_path)

        self._locales = cast(Dict[str, str], cfg["tool"]["oxt"]["locale"]["desc"])

        self._config = Config()
        self._descriptions_path = self._config.build_path / "pkg-desc"
        self._xml_path = self._config.build_path / "description.xml"

    def write(self) -> None:
        """Create the description file for the locales."""
        elements: List[Element] = []

        for key, value in self._locales.items():
            if not value:
                continue
            lang = key.replace("_", "-")
            file_name = f"descr-{lang}.txt"
            elements.append(Element(href=f"pkg-desc/{file_name}", lang=lang))
            out_file = self._descriptions_path / file_name
            self._write_desc_file(out_file, value)
        self._write_xml(elements)

    def _write_desc_file(self, fnm: Path, content: str) -> None:
        """Write the description file."""
        with open(fnm, "w", encoding="utf-8") as f:
            f.write(self._token.process(content))

    def _write_xml(self, elements: List[Element]) -> None:
        """Write the description.xml file."""
        if not elements:
            return
        xml_file = etree.parse(self._xml_path, etree.XMLParser(remove_blank_text=True))
        root = xml_file.getroot()

        descriptions = root.find("{http://openoffice.org/extensions/description/2006}extension-description")
        if descriptions is None:
            descriptions = etree.Element("extension-description", attrib=None, nsmap=None)
            root.append(descriptions)

        for element in elements:
            desc = etree.Element("src", attrib=None, nsmap=root.nsmap)
            desc.set("{http://www.w3.org/1999/xlink}href", element.href)
            desc.set("lang", element.lang)
            descriptions.append(desc)

        xml_file.write(self._xml_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
