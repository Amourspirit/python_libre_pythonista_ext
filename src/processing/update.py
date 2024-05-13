from __future__ import annotations
from pathlib import Path
from ..meta.singleton import Singleton
from ..config import Config
from .token import Token


class Update(metaclass=Singleton):
    def __init__(self) -> None:
        self._config = Config()
        self._update_file = self._config.root_path / "src" / "ext.update.xml"
        self._dist_path = self._config.root_path / self._config.dist_dir_name

    # region Methods
    def _read_text(self) -> str:
        """Reads the text from the update file."""
        with self._update_file.open() as f:
            return f.read()

    def _write_text(self, text: str) -> None:
        """Writes the text to the update file."""
        dest_file = self._dist_path / self._config.update_file  # self._update_file.name
        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(text)

    def process(self) -> None:
        """Processes the update file."""
        token = Token()
        text = self._read_text()
        text = token.process(text)
        self._write_text(text)

    # endregion Methods

    # region Properties
    @property
    def update_file(self) -> Path:
        """The path to the update file."""
        return self._update_file

    # endregion Properties
