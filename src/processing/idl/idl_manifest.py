from __future__ import annotations
from typing import NamedTuple, List
from lxml import etree
from ...config import Config


class Element(NamedTuple):
    """Element of the description file."""

    media_type: str
    full_path: str


class IdlManifest:
    """
    Adds idl rdb files to manifest.

    Rdb files are build from idl files using the IdlRdb class.
    This class finds the rdb files and adds them to the manifest.xml file as file-entry elements.
    """

    def __init__(self) -> None:

        self._config = Config()
        self._rdb_files = list(self._config.build_path.glob("*.rdb"))
        self._xml_path = self._config.build_path / "META-INF" / "manifest.xml"

    def write(self) -> None:
        """Create the description file for the locales."""
        elements: List[Element] = []

        for rdb_file in self._rdb_files:
            elements.append(
                Element(media_type="application/vnd.sun.star.uno-typelibrary;type=RDB", full_path=f"{rdb_file.name}")
            )
        self._write_xml(elements)

    def _write_xml(self, elements: List[Element]) -> None:
        """Write the description.xml file."""
        if not elements:
            return
        tree = etree.parse(self._xml_path, etree.XMLParser(remove_blank_text=True))
        root = tree.getroot()

        # Define the namespace
        # ns = {"manifest": "http://openoffice.org/2001/manifest"}

        for element in elements:
            # Create a new 'manifest:file-entry' element
            # new_element = etree.Element("{http://openoffice.org/2001/manifest}file-entry")
            new_element = etree.Element(
                "{http://openoffice.org/2001/manifest}file-entry", attrib=None, nsmap=root.nsmap
            )
            new_element.set("{http://openoffice.org/2001/manifest}media-type", element.media_type)
            new_element.set("{http://openoffice.org/2001/manifest}full-path", element.full_path)
            root.append(new_element)

        tree.write(self._xml_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
