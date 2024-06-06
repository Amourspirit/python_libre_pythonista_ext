"""
Get all the code for all of the sheets and cells.
The Keys can be a tuple of int, int, int for sheet, row, column.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Set, Tuple
from dataclasses import dataclass, field
import uno
from ooodev.calc import CalcDoc
from ooodev.utils.data_type.cell_obj import CellObj

# if TYPE_CHECKING:


@dataclass
class IndexCellProps:
    props: Set[str]
    index: int = field(default=-1)

    def __hash__(self):
        return hash((self.index, self.props))


class CodeCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CodeCache, cls).__new__(cls)
            cls._instance._is_init = False
        return cls._instance

    def __init__(self):
        if self._is_init:
            return
        self._prop_prefix = "libre_pythonista_"
        self._doc = CalcDoc.from_current_doc()
        self._code = self._get_cells()
        self._cache = {}
        self._previous_cell = None
        self._current_cell = None
        self._current_sheet_index = -1
        self._is_init = True

    def __len__(self) -> int:
        return len(self._code)

    def _get_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        filter_key = f"{self._prop_prefix}codename"
        code_cells = {}
        for sheet in self._doc.sheets:
            code_index = {}
            index = sheet.sheet_index
            # deleted cells will not be in the custom properties
            code_cell = sheet.custom_cell_properties.get_cell_properties(filter_key)
            i = -1
            for key, value in code_cell.items():
                i += 1
                code_index[key] = IndexCellProps(value, i)
            code_cells[index] = code_index
        return code_cells

    def _get_indexes(self, sheet_idx: int = -1) -> Dict[int, CellObj]:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        key = f"{sheet_idx}_indexes"
        if key in self._cache:
            return self._cache[key]
        result = {}
        items = self.code_cells[sheet_idx]
        for cell, props in items.items():
            result[props.index] = cell
        self._cache[key] = result
        return result

    def get_by_index(self, index: int, sheet_idx: int = -1) -> CellObj:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        indexes = self._get_indexes(sheet_idx)
        return indexes[index]

    def get_cell_index(self, cell: CellObj | None = None, sheet_idx: int = -1) -> int:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        if cell is None:
            cell = self.current_cell
        if cell is None:
            raise ValueError("Cell not set")
        items = self.code_cells[sheet_idx]
        if cell not in items:
            return -1
        props = items[cell]
        return props.index

    def get_sheet_cells(self, sheet_idx: int = -1) -> Dict[CellObj, IndexCellProps]:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        return self._code[sheet_idx]

    def get_cell_count(self, sheet_idx: int = -1) -> int:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        return len(self.get_sheet_cells(sheet_idx))

    def has_cell(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        return cell in self._code[sheet_idx]

    def get_first_cell(self, sheet_idx: int) -> CellObj:
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            raise ValueError("No cells in sheet")
        key = f"first_cell_{sheet_idx}"
        if key in self._cache:
            first_cell = self._cache[key]
        else:
            first_cell = self.get_by_index(0, sheet_idx)
            self._cache[key] = first_cell
        return first_cell

    def get_last_cell(self, sheet_idx: int = -1) -> CellObj:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            raise ValueError("No cells in sheet")
        key = f"last_cell_{sheet_idx}"
        if key in self._cache:
            last_cell = self._cache[key]
        else:
            last_cell = self.get_by_index(count - 1, sheet_idx)
            self._cache[key] = last_cell
        return last_cell

    def is_first_cell(self, cell: CellObj | None = None, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        if cell is None:
            cell = self.current_cell
        if cell is None:
            return False
        first_cell = self.get_first_cell(sheet_idx)
        return first_cell == cell

    def is_last_cell(self, cell: CellObj | None = None, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        if cell is None:
            cell = self.current_cell
        if cell is None:
            return False
        last_cell = self.get_last_cell(sheet_idx)
        return last_cell == cell

    def is_before_first(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        first_cell = self.get_first_cell(sheet_idx)
        return cell < first_cell

    def is_after_last(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        last_cell = self.get_last_cell(sheet_idx)
        return cell > last_cell

    def get_next_cell(self, cell: CellObj, sheet_idx: int = -1) -> CellObj | None:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            raise ValueError("Sheet index not set")
        if self.is_last_cell(cell, sheet_idx):
            return None
        index = self.get_cell_index(cell, sheet_idx)
        if index < 0:
            return None
        count = self.get_cell_count(sheet_idx)
        next_index = index + 1
        if next_index >= count - 1:
            return None
        return self.get_by_index(next_index, sheet_idx)

    # region Properties

    @property
    def code_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        return self._code

    @property
    def previous_cell(self) -> CellObj | None:
        return self._previous_cell

    @previous_cell.setter
    def previous_cell(self, cell: CellObj | None) -> None:
        self._previous_cell = cell
        return None

    @property
    def current_cell(self) -> CellObj | None:
        return self._current_cell

    @current_cell.setter
    def current_cell(self, cell: CellObj | None) -> None:
        self.previous_cell = self._current_cell
        self._current_cell = cell
        return None

    @property
    def current_sheet_index(self) -> int:
        return self._current_sheet_index

    @current_sheet_index.setter
    def current_sheet_index(self, index: int) -> None:
        self._current_sheet_index = index
        return None

    # endregion Properties

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
        return None
