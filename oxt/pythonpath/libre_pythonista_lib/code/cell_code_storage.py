"""
Class that manages saving and reading cell code.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import uno
from ooodev.io.sfa import Sfa

_MOD_DIR = "librepythonista"

if TYPE_CHECKING:
    from ooodev.utils.helper.dot_dict import DotDict
    from .py_cell import PyCell


class CellCodeStorage:
    def __init__(self, py_cell: PyCell) -> None:
        self._py_cell = py_cell
        self._sfa = Sfa()
        self._root_uri = f"vnd.sun.star.tdoc:/{self._py_cell.cell.calc_sheet.calc_doc.runtime_uid}/{_MOD_DIR}"
        if not self._sfa.exists(self._root_uri):
            self._sfa.inst.create_folder(self._root_uri)
        self._uri = f"{self._root_uri}/{self._py_cell.cell.calc_sheet.unique_id}/{self._py_cell.code_id}.py"

    def has_code(self) -> bool:
        return self._sfa.exists(self._uri)

    def save_code(self, code: str) -> None:
        self._sfa.write_text_file(self._uri, code)

    def read_code(self) -> str:
        return self._sfa.read_text_file(self._uri)
