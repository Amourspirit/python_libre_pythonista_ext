from __future__ import annotations
from pathlib import Path

from .publisher import Publisher


class PublisherUpdate(Publisher):
    """Reads Locale descriptions from pyproject.toml and writes them to update.xml."""

    def _get_xml_path(self) -> Path:
        return self._config.root_path / self._config.dist_dir_name / self._config.update_file
