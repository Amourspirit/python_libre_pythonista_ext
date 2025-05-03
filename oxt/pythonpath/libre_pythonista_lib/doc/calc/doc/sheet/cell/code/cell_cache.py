"""
Manages a cache of cells containing code across multiple sheets in a Calc document.

The cache maintains information about cells that contain code, including their properties
and relative positions within sheets. It provides methods for navigating between code cells,
managing cell properties, and handling cell address updates.

Key Features:
- Maintains a mapping of sheet indices to cells containing code
- Tracks current and previous cell/sheet positions
- Provides navigation methods (next, previous, first, last cells)
- Handles cell property updates and address synchronization
- Implements singleton pattern per document

The Keys in the cache can be a tuple of (sheet_index, row, column).
"""

# region Imports
from __future__ import annotations
from typing import Any, cast, Dict, Set, TYPE_CHECKING, Iterator, Generator, Union, Optional
from contextlib import contextmanager
from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.args.event_args import EventArgs
from ooodev.events.events import Events
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from ooodev.utils.type_var import EventCallback
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_cells import QryLpCells
    from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.gen_util import GenUtil
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.const import (
        PYTHON_AFTER_ADD_SRC_CODE,
        PYTHON_AFTER_REMOVE_SOURCE_CODE,
    )
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_cells import QryLpCells
    from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.gen_util import GenUtil
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.doc.calc.const import PYTHON_AFTER_ADD_SRC_CODE, PYTHON_AFTER_REMOVE_SOURCE_CODE

# endregion Imports

_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_cache.CellCache"


class CellCache(LogMixin):
    """
    A singleton class that manages a cache of cells containing code across multiple sheets in a Calc document.

    The class maintains state about cells containing code, including their properties and positions.
    It implements the singleton pattern per document, meaning only one instance exists per document.

    Inherits from:
        LogMixin: Provides logging functionality

    Key Features:
        - Singleton implementation per document
        - Tracks current and previous cell positions
        - Maintains sheet indexes
        - Caches cell properties and code information
    """

    # region Create

    def __new__(cls, doc: CalcDoc) -> CellCache:
        """
        Creates or returns existing singleton instance for the given document.

        Args:
            doc (CalcDoc): The Calc document to create/get cache for

        Returns:
            CellCache: The singleton instance for the document
        """
        gbl_cache = DocGlobals.get_current(doc.runtime_uid)
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self, doc: CalcDoc) -> None:
        """
        Initializes the CellCache instance. Only runs once per singleton instance.

        Args:
            doc (CalcDoc): The Calc document to initialize cache for
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self._events = Events(source=self)
        self._shared_event = SharedEvent(doc)
        self._cfg = BasicConfig()
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._code_prop = self._cfg.cell_cp_codename
        self._doc = doc
        self._code_cells = cast(Dict[int, Dict[CellObj, IndexCellProps]], None)
        self._cache = {}
        self._previous_cell = None
        self._current_cell = None
        self._previous_sheet_index = -1
        self._current_sheet_index = -1
        if self.log.is_debug:
            self.log.debug("__init__() for doc: %s", doc.runtime_uid)
            for sheet_idx, items in self.code_cells.items():
                self.log.debug("Sheet Index: %i", sheet_idx)
                for cell, props in items.items():
                    self.log.debug("Cell: %s - Props: %s", cell, props.props)
            self.log.debug("__init__() Code Property: %s", self._code_prop)
        self._init_events()
        self._is_init = True

    # endregion Create
    # region Events

    def _init_events(self) -> None:
        self._fn_on_python_src_code_removed = self.on_python_src_code_removed
        self._fn_on_python_src_code_inserted = self.on_python_src_code_inserted
        self._shared_event.subscribe_event(PYTHON_AFTER_REMOVE_SOURCE_CODE, self._fn_on_python_src_code_removed)
        self._shared_event.subscribe_event(PYTHON_AFTER_ADD_SRC_CODE, self._fn_on_python_src_code_inserted)

    # endregion Events

    # region Event Handlers

    def on_python_src_code_removed(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        # triggered in : libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager.PySourceManager.remove_source
        self.log.debug("on_python_src_code_removed()")
        data = event.event_data
        cell = cast(CalcCell, data.cell)
        sheet_idx = cast(int, data.sheet_idx)
        self.remove_cell(cell=cell.cell_obj, sheet_idx=sheet_idx)

    def on_python_src_code_inserted(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        # triggered in : libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager.PySourceManager.add_source
        self.log.debug("on_python_src_code_inserted()")
        data = event.event_data
        cell = cast(CalcCell, data.cell)
        code_name = cast(str, data.code_name)
        sheet_idx = cast(int, data.sheet_idx)
        self.insert(cell=cell.cell_obj, code_name=code_name, props={self.code_prop}, sheet_idx=sheet_idx)

    # endregion Event Handlers

    # region Dunder Methods

    def __len__(self) -> int:
        return len(self.code_cells)

    def __iter__(self) -> Iterator[int]:
        return iter(self.code_cells)

    # endregion Dunder Methods

    # region Public Methods

    def get_cell_before(self, cell: Optional[CellObj] = None, sheet_idx: int = -1) -> Union[CellObj, None]:
        """
        Gets the cell before the current cell if Any.

        Args:
            cell (CellObj, optional): Cell. Defaults to ``current_cell``.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Cell not set.
            ValueError: Sheet index not set.

        Returns:
            CellObj, None: Cell before the current cell if Any; Otherwise, ``None``
        """
        if cell is None:
            cell = self.current_cell
        if cell is None:
            self.log.error("get_cell_before() Cell not set")
            raise ValueError("Cell not set")
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_cell_before() Sheet index not set")
            raise ValueError("Sheet index not set")
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            return None
        # get the index of the current cell if available
        index = self.get_cell_index(cell, sheet_idx)
        if self.log.is_debug:
            self.log.debug("get_cell_before() Index for current cell %s is %i", cell, index)
        if index == 0:
            if self.log.is_debug:
                self.log.debug("get_cell_before() Current cell %s is the first cell", cell)
            return None
        if index > 0:
            co = self.get_by_index(index - 1, sheet_idx)
            if self.log.is_debug:
                self.log.debug("get_cell_before() Cell before current cell %s is %s", cell, co)
            return co
        # negative index means the cell is not in this instance.
        items = self.code_cells[sheet_idx]
        found = None
        cell_objs = list(items.keys())
        cell_objs.sort()
        for co in cell_objs:
            if co >= cell:
                break
            found = co
        if self.log.is_debug:
            self.log.debug("get_cell_before() Cell found before current cell %s is %s", cell, found)
        return found

    def get_cell_complete_count(self) -> int:
        """
        Get the total number of cells in all the sheets.

        Returns:
            int: Total number of cells in all the sheets.
        """
        sheets_count = len(self.code_cells)
        count = 0
        for i in range(sheets_count):
            sheet = self.code_cells[i]
            count += len(sheet)
        return count

    def get_cell_count(self, sheet_idx: int = -1) -> int:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_cell_count() Sheet index not set")
            raise ValueError("Sheet index not set")
        return len(self.get_sheet_cells(sheet_idx))

    def get_by_index(self, index: int, sheet_idx: int = -1) -> CellObj:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_by_index() Sheet index not set")
            raise ValueError("Sheet index not set")
        if self.log.is_debug:
            self.log.debug("get_by_index() Index: %i - Sheet Index: %i", index, sheet_idx)
        self._ensure_sheet_index(sheet_idx)
        indexes = self._get_indexes(sheet_idx)
        if self.log.is_debug:
            for key, value in indexes.items():
                self.log.debug("get_by_index() Index: %i - Cell: %s", key, value)
        if index not in indexes:
            self.log.error("get_by_index() Index: %i not in indexes", index)
            raise ValueError(f"Index: {index} not in indexes")
        return indexes[index]

    def get_cell_index(self, cell: Optional[CellObj] = None, sheet_idx: int = -1) -> int:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_cell_index() Sheet index not set")
            raise ValueError("Sheet index not set")
        if cell is None:
            cell = self.current_cell
        if cell is None:
            self.log.error("get_cell_index() Cell not set")
            raise ValueError("Cell not set")
        items = self.code_cells[sheet_idx]
        if cell not in items:
            self.log.debug(f"get_cell_index() Cell: {cell} not in sheet index: {sheet_idx}")
            return -1
        props = items[cell]
        return props.index

    def get_first_cell(self, sheet_idx: int = -1) -> CellObj:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_first_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            self.log.error("get_first_cell() No cells in sheet")
            raise ValueError("No cells in sheet")
        key = f"first_cell_{sheet_idx}"
        if key in self._cache:
            first_cell = self._cache[key]
        else:
            first_cell = self.get_by_index(0, sheet_idx)
            self._cache[key] = first_cell
        return first_cell

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
            self.log.error("get_index_cell_props() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_cell(cell, sheet_idx):
            self.log.error("get_index_cell_props() Cell: %s not in sheet index: %i", cell, sheet_idx)
            raise ValueError(f"Cell: {cell} not in sheet index: {sheet_idx}")
        return self.code_cells[sheet_idx][cell]

    def get_last_cell(self, sheet_idx: int = -1) -> CellObj:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_last_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        count = self.get_cell_count(sheet_idx)
        if count == 0:
            self.log.error("get_last_cell() No cells in sheet")
            raise ValueError("No cells in sheet")
        key = f"last_cell_{sheet_idx}"
        if key in self._cache:
            last_cell = self._cache[key]
        else:
            last_cell = self.get_by_index(count - 1, sheet_idx)
            self._cache[key] = last_cell
        return last_cell

    def get_next_cell(self, cell: Optional[CellObj] = None, sheet_idx: int = -1) -> Union[CellObj, None]:
        if cell is None:
            cell = self.current_cell
        if cell is None:
            self.log.error("get_next_cell() Cell not set")
            raise ValueError("Cell not set")
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_next_cell() Sheet index not set")
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

    def get_sheet_cells(self, sheet_idx: int = -1) -> Dict[CellObj, IndexCellProps]:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("get_sheet_cells() Sheet index not set")
            raise ValueError("Sheet index not set")
        return self.code_cells[sheet_idx]

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
            self.log.error("has_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_sheet(sheet_idx):
            self.log.debug("has_cell() Sheet index %i not in code", sheet_idx)
            return False
        return cell in self.code_cells[sheet_idx]

    def has_sheet(self, sheet_idx: int) -> bool:
        """
        Gets if the current instance has a sheet index.

        Args:
            sheet_idx (int): Sheet Index - Zero Based.
        """
        return sheet_idx in self.code_cells

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
            self.log.error("insert() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        if self.has_cell(cell, sheet_idx):
            self.log.error("insert() Cell already exists")
            raise ValueError("Cell already exists")
        if self._code_prop not in props:
            self.log.error("insert() Code property '%s' not in props", self._code_prop)
            raise ValueError("Code property '%s' not in props", self._code_prop)
        self.log.debug(
            "insert() Inserting Cell: %s into Sheet Index: %i with Code Name: %s",
            cell,
            sheet_idx,
            code_name,
        )
        self.code_cells[sheet_idx][cell] = IndexCellProps(code_name, props)
        self._update_indexes()
        self.log.debug(
            "insert() Inserted Cell: %s into Sheet Index: %i with Code Name: %s",
            cell,
            sheet_idx,
            code_name,
        )
        if "code_name_map" in self._cache:
            self.log.debug("insert() Removing code_name_map from cache")
            del self._cache["code_name_map"]
        return None

    def is_after_last(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("is_after_last() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        last_cell = self.get_last_cell(sheet_idx)
        return cell > last_cell

    def is_before_first(self, cell: CellObj, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("is_before_first() Sheet index not set")
            raise ValueError("Sheet index not set")
        self._ensure_sheet_index(sheet_idx)
        first_cell = self.get_first_cell(sheet_idx)
        return cell < first_cell

    def is_first_cell(self, cell: Optional[CellObj] = None, sheet_idx: int = -1) -> bool:
        """
        Gets if cell is equal to the first cell in the sheet.

        Args:
            cell (CellObj, None, optional): Cell. Defaults to ``current_cell``.
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Raises:
            ValueError: Sheet index not set

        Returns:
            bool: ``True`` if cell is equal to the first cell in the sheet or if there are no cells in the sheet; Otherwise, ``False``.
        """
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("is_first_cell() Sheet index not set")
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

    def is_last_cell(self, cell: Optional[CellObj] = None, sheet_idx: int = -1) -> bool:
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("is_last_cell() Sheet index not set")
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
        self.log.debug("remove_cell() Removing Cell: %s from sheet index: %i", cell, sheet_idx)
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("remove_cell() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_cell(cell, sheet_idx):
            self.log.error("remove_cell() Cell: %s not in sheet index: %i", cell, sheet_idx)
            return
        del self.code_cells[sheet_idx][cell]
        self.log.debug(
            "remove_cell() Removed Cell: %s from sheet index: %i",
            cell,
            sheet_idx,
        )
        self._update_indexes()
        if "code_name_map" in self._cache:
            del self._cache["code_name_map"]
        return None

    def update_sheet_cell_addr_prop(self, sheet_idx: int = -1) -> None:
        """
        Updates the cell address custom property for the cells in the sheet.

        Args:
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Warning:
            This method need to be run on a up to date cell cache.
            Usually ``reset_instance`` is call before running this method.
        """
        is_db = self.log.is_debug
        if is_db:
            self.log.debug("update_sheet_cell_addr_prop() for Sheet Index: %i", sheet_idx)
        if sheet_idx < 0:
            sheet_idx = self.current_sheet_index
        if sheet_idx < 0:
            self.log.error("insert() Sheet index not set")
            raise ValueError("Sheet index not set")

        sheet = self._doc.sheets[sheet_idx]
        for cell, icp in self.code_cells[sheet_idx].items():
            calc_cell = sheet[cell]
            if is_db:
                self.log.debug("update_sheet_cell_addr_prop() for Cell: %s", cell)
            addr_str = GenUtil.create_cell_addr_query_str(sheet_idx, str(calc_cell.cell_obj))
            addr = Addr(addr_str)

            qry = QryAddr(calc_cell)
            qry_result = self._qry_handler.handle(qry)
            if Result.is_failure(qry_result):
                self.log.warning("update_sheet_cell_addr_prop() Failed to get cell address property for %s", cell)
                continue
            current = qry_result.data

            if current != addr:
                cmd = CmdAddr(calc_cell, addr)
                self._cmd_handler.handle(cmd)
                if not cmd.success:
                    self.log.error("update_sheet_cell_addr_prop() Failed to update cell address property for %s", cell)
                    continue

                args = EventArgs(self)
                args.event_data = DotDict(
                    calc_cell=calc_cell,
                    sheet_idx=sheet_idx,
                    old_addr=current,
                    addr=addr,
                    icp=icp,
                )
                self._events.trigger_event("update_sheet_cell_addr_prop()", args)
        if is_db:
            self.log.debug("update_sheet_cell_addr_prop() Done")
        return None

    # endregion Public Methods

    # region Private Methods

    def _qry_lp_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        qry = QryLpCells(doc=self._doc)
        return self._qry_handler.handle(qry)

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

    def _update_indexes(self) -> None:
        self.log.debug("_update_indexes() Updating Indexes")
        count = 0
        for sheet_idx in self.code_cells:
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
        self.log.debug("_update_indexes() %i Indexes Updated", count)

    def _ensure_sheet_index(self, sheet_idx: int) -> None:
        self.log.debug("_ensure_sheet_index() Sheet Index: %s", sheet_idx)
        if sheet_idx < 0:
            self.log.error("_ensure_sheet_index() Sheet index not set")
            raise ValueError("Sheet index not set")
        if not self.has_sheet(sheet_idx):
            self.log.debug("_ensure_sheet_index() Sheet index %i not in code. Adding.", sheet_idx)
            self.code_cells[sheet_idx] = {}

    # endregion Private Methods

    # region Context Manager
    # make a context manager method that will set the current cell and sheet index
    # and reset them when done
    @contextmanager
    def set_context(self, cell: CellObj, sheet_idx: int) -> Generator[None, Any, None]:
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

    # endregion Context Manager

    # region Events
    def subscribe_cell_addr_prop_update(self, cb: EventCallback) -> None:
        """
        Subscribe to the update_sheet_cell_addr_prop event.

        Args:
            cb (EventCallback): Event Callback.
        """
        self._events.subscribe_event("update_sheet_cell_addr_prop", cb)

    def unsubscribe_cell_addr_prop_update(self, cb: EventCallback) -> None:
        """
        Un-subscribe from the update_sheet_cell_addr_prop event.

        Args:
            cb (EventCallback): Event Callback.
        """
        self._events.unsubscribe_event("update_sheet_cell_addr_prop", cb)

    # endregion Events_KEY

    # region Cache
    def clear_instance_cache(self) -> None:
        """
        Clears the instance cache.
        """
        gbl_cache = DocGlobals.get_current(uid=self._doc.runtime_uid)

        if _KEY in gbl_cache.mem_cache:
            del gbl_cache.mem_cache[_KEY]
            self.log.debug("clear_instance_cache() - Cleared instance cache.")

    # endregion Cache

    # region Properties

    @property
    def code_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        """
        Gets the code cells.

        This is a dictionary of dictionaries. The key is the sheet index and the value is a dictionary of cells and their properties.
        """
        if self._code_cells is None:
            self._code_cells = self._qry_lp_cells()
        return self._code_cells

    @property
    def code_name_cell_map(self) -> Dict[str, CellObj]:
        """
        Gets a dictionary of code name to cell object.

        Because cell code names are unique this is a one to one mapping.
        """
        if "code_name_map" in self._cache:
            return self._cache["code_name_map"]
        result = {}
        for _, items in self.code_cells.items():
            for cell, props in items.items():
                result[props.code_name] = cell
        self._cache["code_name_map"] = result
        return result

    @property
    def previous_cell(self) -> Union[CellObj, None]:
        return self._previous_cell

    @previous_cell.setter
    def previous_cell(self, cell: Optional[CellObj]) -> None:
        self._previous_cell = cell
        return None

    @property
    def current_cell(self) -> Union[CellObj, None]:
        return self._current_cell

    @current_cell.setter
    def current_cell(self, value: Optional[CellObj]) -> None:
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
