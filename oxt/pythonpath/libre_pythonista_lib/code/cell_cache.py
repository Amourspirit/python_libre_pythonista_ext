"""
Get all the code for all of the sheets and cells.
The Keys can be a tuple of int, int, int for sheet, row, column.
"""

from __future__ import annotations
from typing import Dict, Set, TYPE_CHECKING
from contextlib import contextmanager
from dataclasses import dataclass, field
import uno
from ooodev.calc import CalcDoc
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


@dataclass
class IndexCellProps:
    code_name: str
    props: Set[str]
    index: int = field(default=-1)

    def __hash__(self):
        return hash((self.index, self.props))


class CellCache:
    _instances = {}

    def __new__(cls, doc: CalcDoc):
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            cls._instances[key] = super(CellCache, cls).__new__(cls)
            cls._instances[key]._is_init = False
        return cls._instances[key]

    def __init__(self, doc: CalcDoc):
        is_init = getattr(self, "_is_init", False)
        if is_init:
            return
        self._cfg = Config()
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._code_prop = self._cfg.cell_cp_codename
        self._doc = doc
        self._code = self._get_cells()
        self._cache = {}
        self._previous_cell = None
        self._current_cell = None
        self._previous_sheet_index = -1
        self._current_sheet_index = -1
        if self._log.is_debug:
            self._log.debug(f"__init__() for doc: {doc.runtime_uid}")
            for sheet_idx, items in self._code.items():
                self._log.debug(f"Sheet Index: {sheet_idx}")
                for cell, props in items.items():
                    self._log.debug(f"Cell: {cell} - Props: {props.props}")
            self._log.debug(f"__init__() Code Property: {self._code_prop}")
        self._is_init = True

    def __len__(self) -> int:
        return len(self._code)

    def get_cell_complete_count(self) -> int:
        """
        Get the total number of cells in all the sheets.

        Returns:
            int: Total number of cells in all the sheets.
        """
        sheets_count = len(self._code)
        count = 0
        for i in range(sheets_count):
            sheet = self._code[i]
            count += len(sheet)
        return count

    def _get_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        filter_key = self._code_prop
        code_cells = {}
        for sheet in self._doc.sheets:
            code_index = {}
            index = sheet.sheet_index
            # deleted cells will not be in the custom properties

            code_cell = sheet.custom_cell_properties.get_cell_properties(filter_key)
            i = -1
            for key, value in code_cell.items():
                i += 1
                cell = sheet[key]
                code_name = cell.get_custom_property(filter_key, "")
                if not code_name:
                    self._log.error(f"_get_cells() Code Name not found for cell: {cell}. Skipping?")
                    continue
                code_index[key] = IndexCellProps(code_name, value, i)
            code_cells[index] = code_index
        return code_cells

    def _ensure_sheet_index(self, sheet_idx: int) -> None:
        if sheet_idx < 0:
            self._log.error("_ensure_sheet_index() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_sheet(sheet_idx):
            self._log.debug(f"_ensure_sheet_index() Sheet index {sheet_idx} not in code. Adding.")
            self._code[sheet_idx] = {}

    def insert(self, cell: CellObj, code_name: str, props: Set[str], sheet_idx: int = -1) -> None:
        """
        Insert a new cell into the cache and updates the indexes. If the sheet index is not in the cache it is added.

        Args:
            cell (CellObj): Cell Object.
            code_name (str): The Code Name. This is the name for the custom property ``libre_pythonista_codename``.
            props (Set[str]): The Cell Property Names.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: If cell already exist

        Returns:
            None:

        Note:
            Reading the sheet custom cell properties from the sheets is a bit slow. Allowing the insertion rather then reloading the custom properties is faster.
        """
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("insert() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        if self.has_cell(cell, sheet_idx):
            self._log.error("insert() Cell already exists")
            raise ValueError("Cell already exists")
        if self._code_prop not in props:
            self._log.error(f"insert() Code property '{self._code_prop}' not in props")
            raise ValueError(f"Code property '{self._code_prop}' not in props")
        self._log.debug(f"insert() Inserting Cell: {cell} into Sheet Index: {sheet_idx} with Code Name: {code_name}")
        self._code[sheet_idx][cell] = IndexCellProps(code_name, props)
        self._update_indexes()
        self._log.debug(f"insert() Inserted Cell: {cell} into Sheet Index: {sheet_idx} with Code Name: {code_name}")
        if "code_name_map" in self._cache:
            self._log.debug("insert() Removing code_name_map from cache")
            del self._cache["code_name_map"]
        return None

    def remove_cell(self, cell: CellObj, sheet_idx: int = -1) -> None:
        """
        Removes a cell from the cache and updates the indexes.

        Args:
            cell (CellObj): Cell Object.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Sheet index not set

        Returns:
            None:

        Note:
            Reading the sheet custom cell properties from the sheets is a bit slow. Allowing the deletion rather then reloading the custom properties is faster.
        """
        self._log.debug(f"remove_cell() Removing Cell: {cell} from sheet index: {sheet_idx}")
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("remove_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_cell(cell, sheet_idx):
            self._log.error(f"remove_cell() Cell: {cell} not in sheet index: {sheet_idx}")
            return
        del self._code[sheet_idx][cell]
        self._log.debug(f"remove_cell() Removed Cell: {cell} from sheet index: {sheet_idx}")
        self._update_indexes()
        if "code_name_map" in self._cache:
            del self._cache["code_name_map"]
        return None

    def get_index_cell_props(self, cell: CellObj, sheet_idx: int = -1) -> IndexCellProps:
        """
        Get the IndexCellProps for the cell.

        Args:
            cell (CellObj): Cell Object.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Sheet index not set
            ValueError: Cell not in sheet index

        Returns:
            IndexCellProps: IndexCellProps for the cell.
        """
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_index_cell_props() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_cell(cell, sheet_idx):
            self._log.error(f"get_index_cell_props() Cell: {cell} not in sheet index: {sheet_idx}")
            raise ValueError(f"Cell: {cell} not in sheet index: {sheet_idx}")
        return self._code[sheet_idx][cell]

    def _update_indexes(self) -> None:
        self._log.debug("_update_indexes() Updating Indexes")
        count = 0
        for sheet_idx in self._code.keys():
            i = -1
            items = self.code_cells[sheet_idx]
            for itm in items.values():
                i += 1
                itm.index = i
                count += 1

            # clear the cache for the indexes
            key = f"{sheet_idx}_indexes"
            if key in self._cache:
                del self._cache[key]
        self._log.debug(f"_update_indexes() {count} Indexes Updated")

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
            self._log.error("get_by_index() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        indexes = self._get_indexes(sheet_idx)
        if self._log.is_debug:
            for key, value in indexes.items():
                self._log.debug(f"get_by_index() Index: {key} - Cell: {value}")
        if index not in indexes:
            self._log.error(f"get_by_index() Index: {index} not in indexes")
            raise ValueError(f"Index: {index} not in indexes")
        return indexes[index]

    def get_cell_index(self, cell: CellObj | None = None, sheet_idx: int = -1) -> int:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_cell_index() Sheet index not set")
            raise ValueError("Sheet index not set")
        if cell is None:
            cell = self.current_cell
        if cell is None:
            self._log.error("get_cell_index() Cell not set")
            raise ValueError("Cell not set")
        items = self.code_cells[sheet_idx]
        if cell not in items:
            self._log.debug(f"get_cell_index() Cell: {cell} not in sheet index: {sheet_idx}")
            return -1
        props = items[cell]
        return props.index

    def get_sheet_cells(self, sheet_idx: int = -1) -> Dict[CellObj, IndexCellProps]:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_sheet_cells() Sheet index not set")
            raise ValueError("Sheet index not set")
        return self._code[sheet_idx]

    def get_cell_count(self, sheet_idx: int = -1) -> int:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_cell_count() Sheet index not set")
            raise ValueError("Sheet index not set")
        return len(self.get_sheet_cells(sheet_idx))

    def has_sheet(self, sheet_idx: int) -> bool:
        """
        Gets if the current instance has a sheet index.

        Args:
            sheet_idx (int): Sheet Index - Zero Based.
        """
        return sheet_idx in self._code

    def has_cell(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        """
        Gets if the current instance as a cell.

        Args:
            cell (CellObj): Cell Object.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Sheet index not set

        Returns:
            bool: ``True`` if the cell is in the current instance; Otherwise, ``False``.

        Note:
            If the sheet index in not in the current instance then ``False`` is returned.
        """
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("has_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_sheet(sheet_idx):
            self._log.debug(f"has_cell() Sheet index {sheet_idx} not in code")
            return False
        return cell in self._code[sheet_idx]

    def get_first_cell(self, sheet_idx: int = -1) -> CellObj:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_first_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            self._log.error("get_first_cell() No cells in sheet")
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
            self._log.error("get_last_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            self._log.error("get_last_cell() No cells in sheet")
            raise ValueError("No cells in sheet")
        key = f"last_cell_{sheet_idx}"
        if key in self._cache:
            last_cell = self._cache[key]
        else:
            last_cell = self.get_by_index(count - 1, sheet_idx)
            self._cache[key] = last_cell
        return last_cell

    def is_first_cell(self, cell: CellObj | None = None, sheet_idx: int = -1) -> bool:
        """
        Gets if cell is equal to the first cell in the sheet.

        Args:
            cell (CellObj | None, optional): Cell. Defaults to ``current_cell``.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Sheet index not set

        Returns:
            bool: ``True`` if cell is equal to the first cell in the sheet or if there are no cells in the sheet; Otherwise, ``False``.
        """
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("is_first_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        if cell is None:
            cell = self.current_cell
        if cell is None:
            return False
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            return True
        first_cell = self.get_first_cell(sheet_idx)
        return first_cell == cell

    def is_last_cell(self, cell: CellObj | None = None, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("is_last_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            return True

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
            self._log.error("is_before_first() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        first_cell = self.get_first_cell(sheet_idx)
        return cell < first_cell

    def is_after_last(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("is_after_last() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        last_cell = self.get_last_cell(sheet_idx)
        return cell > last_cell

    def get_next_cell(self, cell: CellObj | None = None, sheet_idx: int = -1) -> CellObj | None:
        if cell is None:
            cell = self.current_cell
        if cell is None:
            self._log.error("get_next_cell() Cell not set")
            raise ValueError("Cell not set")
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_next_cell() Sheet index not set")
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

    def get_cell_before(self, cell: CellObj | None = None, sheet_idx: int = -1) -> CellObj | None:
        """
        Gets the cell before the current cell if Any.

        Args:
            cell (CellObj, optional): Cell. Defaults to ``current_cell``.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Cell not set.
            ValueError: Sheet index not set.

        Returns:
            CellObj | None: Cell before the current cell if Any; Otherwise, ``None``
        """
        if cell is None:
            cell = self.current_cell
        if cell is None:
            self._log.error("get_cell_before() Cell not set")
            raise ValueError("Cell not set")
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self._log.error("get_cell_before() Sheet index not set")
            raise ValueError("Sheet index not set")
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            return None
        # get the index of the current cell if available
        index = self.get_cell_index(cell, sheet_idx)
        if index == 0:
            return None
        if index > 0:
            return self.get_by_index(index - 1, sheet_idx)
        # negative index means the cell is not in this instance.
        items = self.code_cells[sheet_idx]
        found = None
        for key in reversed(items.keys()):
            if key < cell:
                found = key
                break
        return found

    # make a context manager method that will set the current cell and sheet index
    # and reset them when done
    @contextmanager
    def set_context(self, cell: CellObj, sheet_idx: int):
        cur_cell = self.current_cell
        cur_sheet_idx = self.current_sheet_index
        prev_cell = self.previous_cell
        prev_sheet_idx = self.previous_sheet_index
        self.current_cell = cell
        self.current_sheet_index = sheet_idx
        try:
            yield
        finally:
            self.current_cell = cur_cell
            self.current_sheet_index = cur_sheet_idx
            self.previous_cell = prev_cell
            self.previous_sheet_index = prev_sheet_idx

    # region Properties

    @property
    def code_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        """
        Gets the code cells.

        This is a dictionary of dictionaries. The key is the sheet index and the value is a dictionary of cells and their properties.
        """
        return self._code

    @property
    def code_name_cell_map(self) -> Dict[str, CellObj]:
        """
        Gets a dictionary of code name to cell object.

        Because cell code names are unique this is a one to one mapping.
        """
        if "code_name_map" in self._cache:
            return self._cache["code_name_map"]
        result = {}
        for _, items in self._code.items():
            for cell, props in items.items():
                result[props.code_name] = cell
        self._cache["code_name_map"] = result
        return result

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
    def current_cell(self, value: CellObj | None) -> None:
        self.previous_cell = self._current_cell
        self._current_cell = value
        return None

    @property
    def current_sheet_index(self) -> int:
        return self._current_sheet_index

    @current_sheet_index.setter
    def current_sheet_index(self, value: int) -> None:
        self.previous_sheet_index = self._current_sheet_index
        self._current_sheet_index = value
        return None

    @property
    def previous_sheet_index(self) -> int:
        return self._previous_sheet_index

    @previous_sheet_index.setter
    def previous_sheet_index(self, index: int) -> None:
        self._previous_sheet_index = index
        return None

    @property
    def code_prop(self) -> str:
        """Gets the name of the property that contains the python code storage name."""
        return self._code_prop

    # endregion Properties

    @classmethod
    def reset_instance(cls, doc: CalcDoc | None = None) -> None:
        """
        Reset the cached instance(s).

        Args:
            doc (CalcDoc | None, optional): Calc Doc or None. If None all cached instances are cleared. Defaults to None.
        """
        if doc is None:
            cls._instances = {}
            return
        key = f"doc_{doc.runtime_uid}"
        if key in cls._instances:
            del cls._instances[key]
