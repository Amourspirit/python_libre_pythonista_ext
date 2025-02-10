from __future__ import annotations
from typing import TYPE_CHECKING
from pytest_mock import MockerFixture

import pytest


@pytest.fixture(scope="function")
def py_src_mocks(build_setup, mocker: MockerFixture):  # noqa: ANN001, ANN201
    _ = mocker.patch("libre_pythonista_lib.pyc.code.py_source.OxtLogger")


@pytest.fixture(scope="function")
def py_src_provider(py_src_mocks):  # noqa: ANN001, ANN201
    if TYPE_CHECKING:
        from ....oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySrcProvider
    else:
        from libre_pythonista_lib.pyc.code.py_source import PySrcProvider

    class DumbSrcProvider(PySrcProvider):
        def __init__(self, uri: str, src: str) -> None:
            super().__init__(uri)
            self._src = src

        def del_source(self) -> None:
            self._src = ""

        def get_source(self) -> str:
            return self._src

        def set_source(self, code: str) -> None:
            self._src = code

        def exists(self) -> bool:
            return self._src != ""

        def ensure_src(self) -> None:
            pass

    def wrapper(src_data: str) -> DumbSrcProvider:
        return DumbSrcProvider("uri", src_data)

    return wrapper
