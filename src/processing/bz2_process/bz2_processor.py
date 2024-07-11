from __future__ import annotations
import toml
import json
from typing import cast, Dict, TypedDict

import toml
from ...meta.singleton import Singleton
from ...config import Config
from ..token import Token
from ... import file_util


class B2ZConfigT(TypedDict):
    url: str
    md5: str


class BZ2Processor(metaclass=Singleton):
    def __init__(self) -> None:
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        self._toml_dict = toml.load(toml_path)
        self._dict = {}
        config = Config()
        token = Token()
        config_path = config.build_path / token.get_token_value("lo_pip") / "bz2_config"
        if not config_path.exists():
            config_path.mkdir()
        self._json_config_path = config_path / "bz2_config.json"

    def _process(self, bit_key: str) -> None:
        values = cast(Dict[str, B2ZConfigT], self._toml_dict["tool"]["oxt"]["bz2"][bit_key])
        self._dict[bit_key] = {}

        for key, value in values.items():
            self._dict[bit_key].update({key: value})

    def _process_64_bit(self) -> None:
        pass

    def process(self) -> None:
        self._process("32_bit")
        self._process("64_bit")

        with open(self._json_config_path, "w", encoding="utf-8") as f:
            json.dump(self._dict, f, indent=4)
