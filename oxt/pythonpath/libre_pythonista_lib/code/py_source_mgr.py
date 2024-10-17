from __future__ import annotations
from typing import Any, List, Dict, Tuple, TYPE_CHECKING

from sortedcontainers import SortedDict
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils import gen_util as gUtil
from ooodev.io.sfa import Sfa
from ooodev.events.lo_events import LoEvents
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs

# from ooodev.io.log.named_logger import NamedLogger
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.string.str_list import StrList
from ..event.shared_event import SharedEvent
from ..log.log_inst import LogInst
from ..utils.gen_util import GenUtil

# from libre_pythonista.oxt_logger.oxt_logger import OxtLogger
from .py_module import PyModule
from .cell_cache import CellCache
from ..cell.props.key_maker import KeyMaker
from ..const.event_const import GBL_DOC_CLOSING

# from .cell_code_storage import CellCodeStorage

if TYPE_CHECKING:
    from ooodev.utils.type_var import EventCallback
    from logging import Logger
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

_MOD_DIR = "librepythonista"


class PySource:
    def __init__(self, uri: str, unique_id: str, cell: CellObj, mgr: PySourceManager) -> None:
        if getattr(self, "_is_init", False):
            return
        self._uri = uri
        self._cell_obj = cell
        self._mgr = mgr
        self._mod_dict = mgr.py_mod.mod.__dict__.copy()
        # pth = Path(uri)
        # self._name = pth.stem
        self._row = cell.row - 1
        self._col = cell.col_obj.index
        self._sheet_idx = cell.sheet_idx
        self._src_code = None
        self._dd_data = DotDict(data=None, py_src=self)
        self._unique_id = unique_id
        self._is_init = True

    def __lt__(self, other: Any):
        # for sort
        if isinstance(other, PySource):
            addr1 = (self.sheet_idx, self.row, self.col)
            addr2 = (other.sheet_idx, other.row, other.col)
            return addr1 < addr2
        return NotImplemented

    def _get_source(self) -> str:
        """Reads the source code from the file. This method does not cache the source code"""
        self._mgr.log.debug("PySource._get_source() - Getting Source")
        if not self.exists():
            self._mgr.log.debug(
                f"PySource._get_source() - Source file does not exist: {self._uri}. Returning empty string."
            )
            return ""
        return self._mgr.sfa.read_text_file(self._uri)

    def _set_source(self, code: str, mode: str = "w") -> None:
        """Writes the source code to the file."""
        self._mgr.log.debug("PySource._set_source() - Setting Source")
        self._mgr.ensure_src_folder()
        self._mgr.sfa.write_text_file(self._uri, code, mode)

    def del_source(self) -> None:
        """Deletes the source file."""
        self._mgr.log.debug("PySource.del_source() - Deleting Source")
        if self.exists():
            self._mgr.sfa.delete_file(self._uri)
        else:
            self._mgr.log.debug("PySource.del_source() - Source folder does not exist.")

    def exists(self) -> bool:
        return self._mgr.sfa.exists(self._uri)

    # @property
    # def name(self) -> str:
    #     return self._name

    @property
    def col(self) -> int:
        """Column zero based index."""
        return self._col

    @property
    def row(self) -> int:
        """Cell row zero based index."""
        return self._row

    @property
    def sheet_idx(self) -> int:
        """Sheet index zero based."""
        return self._sheet_idx

    @property
    def source_code(self) -> str:
        """Gets/Sets the source code from the file. This value is cached after the first call."""
        if self._src_code is None:
            self._src_code = self._get_source()
        return self._src_code

    @source_code.setter
    def source_code(self, code: str) -> None:
        self._set_source(code)
        self._src_code = code

    @property
    def mod_dict(self) -> Dict[str, Any]:
        return self._mod_dict

    @mod_dict.setter
    def mod_dict(self, value: Dict[str, Any]) -> None:
        self._mod_dict = value

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def value(self) -> Any:
        return self._dd_data.data

    @property
    def is_error(self) -> bool:
        key = "error"
        if key in self._dd_data:
            return self._dd_data.error
        return False

    @property
    def dd_data(self) -> DotDict:
        return self._dd_data

    @dd_data.setter
    def dd_data(self, value: DotDict) -> None:
        self._dd_data = value


class PySourceManager(EventsPartial):
    """
    Python Source code manager.

    Internally data is stored with key in the format of (row, col) and value as PySource object.
    All public facing methods are in the format of (col, row) for cell address because this is how it normally is in Calc.
    """

    # region Init
    def __init__(self, doc: CalcDoc) -> None:
        if getattr(self, "_is_init", False):
            return
        EventsPartial.__init__(self)
        # don't use CalcDoc.from_current_doc() because there many be multiple documents opened already.
        self._doc = doc

        # self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._log = self._get_logger()
        with self._log.indent(True):
            self._log.debug("Init")
        self._sfa = Sfa()

        self._root_uri = f"vnd.sun.star.tdoc:/{self._doc.runtime_uid}/{_MOD_DIR}"
        # if not self._sfa.exists(self._root_uri):
        #     self._sfa.inst.create_folder(self._root_uri)
        self._mod = PyModule()
        self._data = self._get_sources()
        self._se = SharedEvent(doc)
        self._se.trigger_event("PySourceManagerCreated", EventArgs(self))
        self._is_init = True

    def is_src_folder_exists(self) -> bool:
        """Checks if the source folder exists."""
        return self._sfa.exists(self._root_uri)

    def ensure_src_folder(self) -> None:
        """Ensures the source folder exists."""
        if not self.is_src_folder_exists():
            self._sfa.inst.create_folder(self._root_uri)

    def dispose(self) -> None:
        if self._se is not None:
            self._se.trigger_event("PySourceManagerDisposed", EventArgs(self))
        self._se = None

    def _get_logger(self) -> OxtLogger:
        # can be patched for testing.
        # from ..log.log_inst import LogInst
        # return LogInst()
        log = OxtLogger(log_name=self.__class__.__name__)
        return log

    def _get_sources(self) -> SortedDict[Tuple[int, int, int], PySource]:

        cc = CellCache(self._doc)
        code_prop_name = cc.code_prop
        result = None
        sources: List[PySource] = []
        for sheet in self._doc.sheets:
            if sheet.sheet_index not in cc.code_cells:
                continue

            cells = cc.code_cells[sheet.sheet_index]
            for cell in cells.keys():
                calc_cell = sheet[cell]
                if not calc_cell.has_custom_property(code_prop_name):
                    continue
                code_id = calc_cell.get_custom_property(code_prop_name)
                uri = f"{self._root_uri}/{sheet.unique_id}/{code_id}.py"

                if not self._sfa.exists(uri):
                    continue
                sources.append(PySource(uri, code_id, cell, self))

            sources.sort()
            result = SortedDict()
            for src in sources:
                result[src.sheet_idx, src.row, src.col] = src
        if result is None:
            result = SortedDict()
        return result

    # endregion Init

    def get_module_source_code(self) -> str:
        """Gets a string that represents the source code of the modules current state."""
        sb = StrList(sep="\n")
        sb.append(f"# Source code for doc: vnd.sun.star.tdoc:/{self._doc.runtime_uid}/")
        for py_src in self._data.values():
            cell_obj = CellObj.from_idx(col_idx=py_src.col, row_idx=py_src.row, sheet_idx=py_src.sheet_idx)
            sb.append(f"# Code for Cell: {cell_obj} of sheet index: {cell_obj.sheet_idx}")
            sb.append(py_src.source_code)
            sb.append()
        return str(sb)

    def dump_module_source_code_to_log(self) -> str:
        """
        Dumps the module source code to the log.

        Returns the current source code.
        """
        with self._log.indent(True):
            src_code = self.get_module_source_code()
            self._log.debug(
                f"dump_module_source_code_to_log() - Module Source Code:\n# Start Dump\n{src_code}\n\n# End Dump"
            )
            # try:
            #     from .mod_fn.lp_log import LpLog

            #     log = LpLog().log
            #     log.debug(
            #         f"PySourceManager - dump_module_source_code_to_log() - Module Source Code:\n# Start Dump\n{src_code}\n\n# End Dump"
            #     )
            #     return src_code
            # except Exception:
            #     self._log.error("PySourceManager - dump_module_source_code_to_log() - Error dumping to LpLog log.")
            return src_code

    # region Event Subscriptions

    def subscribe_before_source_update(self, cb: EventCallback) -> None:
        """
        Subscribe to before source update event.
        This event is triggered multiple time when a series of cells are being updated.
        This event is triggered after `subscribe_before_cell_source_update``

        Event Args are ``CancelEventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self._update_item()
        self.subscribe_event("BeforeSourceUpdate", cb)

    def subscribe_after_cell_source_update(self, cell: Tuple[int, int], cb: EventCallback) -> None:
        """
        Subscribe to after cell source update event.
        This event is similar to ``subscribe_after_source_update`` except is only is triggered
        when the specified cell is updated. This event is triggered before ``subscribe_after_source_update``.

        Event Args are ``EventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.
        - ``result``: Any: Result of the source code execution.

        Args:
            cell (Tuple[int, int]): Cell address colum and row.
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self._update_item()
        self.subscribe_event(f"AfterSourceUpdate_{cell[0]}_{cell[1]}", cb)

    def subscribe_before_cell_source_update(self, cell: Tuple[int, int], cb: EventCallback) -> None:
        """
        Subscribe to before cell source update event.
        This event is similar to ``subscribe_before_source_update`` except is only is triggered
        when the specified cell is updated. This event is triggered before ``subscribe_before_source_update``.

        Event Args are ``CancelEventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cell (Tuple[int, int]): Cell address colum and row.
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self._update_item()
        self.subscribe_event(f"BeforeSourceUpdate_{cell[0]}_{cell[1]}", cb)

    def subscribe_after_source_update(self, cb: EventCallback) -> None:
        """
        Subscribe to after source update event.
        This event is triggered multiple time when a series of cells are being updated.
        This event is triggered after ``subscribe_after_cell_source_update``

        Event Args are ``EventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.
        - ``result``: Any: Result of the source code execution.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self._update_item()
        self.subscribe_event("AfterSourceUpdate", cb)

    def subscribe_before_add_source(self, cb: EventCallback) -> None:
        """
        Subscribe to before add source event.
        This event is triggered when the ``add_source()`` method is called.

        Event Args are ``CancelEventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:


        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.add_source()
        self.subscribe_event("BeforeAddSource", cb)

    def subscribe_after_add_source(self, cb: EventCallback) -> None:
        """
        Subscribe to after add source event.
        This event is triggered when the ``add_source()`` method is called.

        Event Args are ``EventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:


        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.add_source()
        self.subscribe_event("AfterAddSource", cb)

    def subscribe_before_update_source(self, cb: EventCallback) -> None:
        """
        Subscribe to before update source event.
        This event is triggered when the ``update_source()`` method is called.

        Event Args are ``CancelEventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:


        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.update_source()
        self.subscribe_event("BeforeUpdateSource", cb)

    def subscribe_after_update_source(self, cb: EventCallback) -> None:
        """
        Subscribe to after update source event.
        This event is triggered when the ``update_source()`` method is called.

        Event Args are ``EventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:


        - ``source``: PySource: PySource object.
        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``code``: str: Source code.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.update_source()
        self.subscribe_event("AfterUpdateSource", cb)

    def unsubscribe_after_update_source(self, cb: EventCallback) -> None:
        """
        UnSubscribe to after update source event.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.update_source()
        self.unsubscribe_event("AfterUpdateSource", cb)

    def subscribe_before_remove_source(self, cb: EventCallback) -> None:
        """
        Subscribe to before remove source event.
        This event is triggered when the ``remove_source()`` method is called.

        Event Args are ``CancelEventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.remove_source()
        self.subscribe_event("BeforeRemoveSource", cb)

    def subscribe_after_remove_source(self, cb: EventCallback) -> None:
        """
        Subscribe to after remove source event.
        This event is triggered when the ``remove_source()`` method is called.

        Event Args are ``EventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

        - ``col``: [int]: Cell column zero based index.
        - ``row``: [int]: Cell row zero based index.
        - ``sheet``: CalcSheet: CalcSheet object.

        Args:
            cb (EventCallback): Callback.

        Return:
            None:
        """
        # triggered from self.remove_source()
        self.subscribe_event("AfterRemoveSource", cb)

    # endregion Event Subscriptions

    # region Dunder Methods

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: CellObj | Tuple[int, int, int]) -> PySource:
        """
        Gets an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of Sheet, Column and Row

        Returns:
            PySource: Source object
        """
        is_db = self._log.is_debug
        if isinstance(key, CellObj):
            code_cell = self.convert_cell_obj_to_tuple(key)
        else:
            code_cell = (key[0], key[2], key[1])
        if is_db:
            with self._log.indent(True):
                self._log.debug(f"__getitem__() - Code Cell: {code_cell}")
        result = self._data[code_cell]
        if is_db:
            with self._log.indent(True):
                self._log.debug(f"__getitem__() - Result Unique Id: {result.unique_id}")
        return result

    def __setitem__(self, key: CellObj | Tuple[int, int, int], value: PySource) -> None:
        """
        Sets an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of sheet, Column and Row
            value (PySource): Source object
        """
        if isinstance(key, CellObj):
            code_cell = self.convert_cell_obj_to_tuple(key)
        else:
            code_cell = (key[0], key[2], key[1])
        self._data[code_cell] = value

    def __delitem__(self, key: CellObj | Tuple[int, int, int]) -> None:
        """
        Removes an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of sheet, Column and Row
        """
        if isinstance(key, CellObj):
            co = key
        else:
            co = self.convert_tuple_to_cell_obj(key)
        self.remove_source(co)

    def __contains__(self, key: CellObj | Tuple[int, int, int]) -> bool:
        """
        Checks if key exists in the data.

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of sheet, Column and Row

        Returns:
            bool: True if key exists in the data.
        """
        if isinstance(key, CellObj):
            code_cell = self.convert_cell_obj_to_tuple(key)
        else:
            code_cell = (key[0], key[2], key[1])
        return code_cell in self._data

    def __iter__(self):
        return iter(self._data.values())

    # endregion Dunder Methods
    def _is_last_index(self, index: int) -> bool:
        return index == len(self) - 1

    def convert_cell_obj_to_tuple(self, cell: CellObj) -> Tuple[int, int, int]:
        """
        Converts a cell object to a tuple of (sheet index, row, column).

        Args:
            cell (CellObj): Cell object.

        Returns:
            Tuple[int, int, int]: Tuple of (sheet index, row, column).
        """
        col = cell.col_obj.index
        row = cell.row - 1
        sheet_idx = cell.sheet_idx
        return (sheet_idx, row, col)

    def convert_tuple_to_cell_obj(self, cell: Tuple[int, int, int]) -> CellObj:
        """
        Converts a tuple of (sheet index, row, column) to a cell object.

        Args:
            cell (Tuple[int, int, int]): Tuple of (sheet index, column, row).

        Returns:
            CellObj: Cell object.
        """
        return CellObj.from_idx(col_idx=cell[1], row_idx=cell[2], sheet_idx=cell[0])

    # region Source Management

    def add_source(self, code: str, cell: CellObj) -> None:
        """
        Add Source code for the cell.

        Args:
            code (str): Source code
            cell (Tuple[int, int]): Cell address in column and row.

        Raises:
            Exception: If cell already exists in current data.
        """
        with self._log.indent(True):
            # when adding source is should update the whole module unless it is the last cell for the module.
            self._log.debug("add_source() - Adding Source")
            km = KeyMaker()  # singleton
            code_cell = self.convert_cell_obj_to_tuple(cell)
            sheet_idx = code_cell[0]
            row = code_cell[1]
            col = code_cell[2]
            self._log.debug(f"add_source() sheet index: {sheet_idx} col: {col}, row: {row}")
            if code_cell in self._data:
                self._log.error(f"add_source() - Cell {cell} already exists.")
                raise Exception(f"Cell {cell} already exists.")
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(source=self, sheet_idx=sheet_idx, row=row, col=col, code=code, doc=self._doc)
            self.trigger_event("BeforeAddSource", cargs)
            if cargs.cancel:
                return
            cc = CellCache(self._doc)
            code = cargs.event_data.get("code", code)
            sheet = self._doc.sheets[sheet_idx]
            calc_cell = sheet[cell]
            str_id = "id_" + gUtil.Util.generate_random_alpha_numeric(14)
            self._log.debug(f"add_source() - Adding Source ID: {str_id}")
            calc_cell.set_custom_property(cc.code_prop, str_id)

            addr = GenUtil.create_cell_addr_query_str(sheet_idx, str(cell))
            calc_cell.set_custom_property(km.cell_addr_key, addr)
            self._log.debug(f"add_source() - Setting custom property: {km.cell_addr_key} to {addr}")

            name = str_id + ".py"
            uri = f"{self._root_uri}/{sheet.unique_id}/{name}"
            py_src = PySource(uri, str_id, cell, self)
            py_src.source_code = code  # writes code to file
            # after code has been saved to file, update the cell cache
            # resetting is slower than just adding the cell to the cache
            self._log.debug(f"add_source() - inserting for cell {cell}: sheet index: {sheet_idx}")
            cc.insert(cell=cell, code_name=str_id, props={cc.code_prop}, sheet_idx=sheet_idx)
            self._log.debug(f"add_source() - inserted for cell {cell}: sheet index: {sheet_idx}")
            # CellCache.reset_instance()
            self._data[code_cell] = py_src
            index = self.get_index(cell)
            if index < 0:
                self._log.error(f"add_source() - Cell {cell} not found.")
                raise Exception(f"Cell {cell} not found.")
            if self._is_last_index(index):
                self._log.debug(f"add_source() - Last Index, updating from index {index}")
                self.update_from_index(index)
            else:
                self._log.debug(f"add_source() not last index, Updating all")
                self.update_all()
            eargs = EventArgs.from_args(cargs)
            self.trigger_event("AfterAddSource", eargs)
            self._log.debug("Done Adding Source")
        return None

    def update_source(self, code: str, cell: CellObj) -> None:
        """
        Update the source code for the cell.

        Args:
            code (str): Source code
            cell (Tuple[int, int]): Cell address in row and column.

        Raises:
            Exception: If cell does not exist in current data.
        """
        with self._log.indent(True):
            self._log.debug("update_source()")
            # when updating source is should update the whole module unless it is the last cell for the module.
            code_cell = self.convert_cell_obj_to_tuple(cell)
            sheet_idx = code_cell[0]
            row = code_cell[1]
            col = code_cell[2]
            self._log.debug(f"update_source() sheet index: {sheet_idx} col: {col}, row: {row}")

            if code_cell not in self._data:
                raise Exception(f"Cell {cell} does not exists.")
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(source=self, sheet_idx=sheet_idx, row=row, col=col, code=code, doc=self._doc)
            self.trigger_event("BeforeUpdateSource", cargs)
            if cargs.cancel:
                return
            code = cargs.event_data.get("code", code)
            src = self[cell]
            index = self.get_index(cell)
            if index < 0:
                self._log.error(f"update_source() - Cell {cell} not found.")
                raise Exception(f"Cell {cell} not found.")
            src.source_code = code  # writes code to file
            # CellCache.reset_instance()

            if self._is_last_index(index):
                self._log.debug(f"update_source() is last index updating from index {index}")
                self.update_from_index(index)
            else:
                self._log.debug(f"update_source() not last index, Updating all")
                self.update_all()
            eargs = EventArgs.from_args(cargs)
            self.trigger_event("AfterUpdateSource", eargs)
            return None

    def remove_source(self, cell: CellObj) -> None:
        """
        Removes Source for the cell.

        - Deletes the source code.
        - Removes cell from CellCache.
        - Removes the custom property from the cell.
        - Updates the module to reflect the changes.

        Args:
            cell (Tuple[int, int]): Cell address in row and column.
        """
        # when removing even if this was the last cell, the module should be reset.
        # It is possible that the cell that is being removed contained code that modified a previous cell.
        # _update_from_index() will not restore the values of cells that were modified by the cell being removed.
        with self._log.indent(True):
            self._log.debug("remove_source() Entered.")
            code_cell = self.convert_cell_obj_to_tuple(cell)
            sheet_idx = code_cell[0]
            row = code_cell[1]
            col = code_cell[2]
            self._log.debug(f"remove_source() sheet index: {sheet_idx} col: {col}, row: {row}")

            if code_cell not in self._data:
                raise Exception(f"Cell {cell} does not exist.")
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(source=self, sheet_idx=sheet_idx, row=row, col=col, doc=self._doc)
            self.trigger_event("BeforeRemoveSource", cargs)
            if cargs.cancel:
                return
            # triggers are in col row format
            self.trigger_event(f"BeforeRemoveSource_{col}_{row}", cargs)
            if cargs.cancel:
                return
            self._data[code_cell].del_source()
            del self._data[code_cell]
            sheet = self._doc.sheets[sheet_idx]
            calc_cell = sheet[cell]
            cc = CellCache(self._doc)
            cc.remove_cell(cell=cell, sheet_idx=sheet_idx)
            if calc_cell.has_custom_property(cc.code_prop):
                self._log.debug(f"remove_source() Has custom property: {cc.code_prop}. Removing ...")
                calc_cell.remove_custom_property(cc.code_prop)
                self._log.debug("remove_source() custom property removed.")
            # remove the cell from the cache is faster then resetting
            # CellCache.reset_instance()
            self._log.debug("remove_source() Calling update_all()")
            self.update_all()

            eargs = EventArgs.from_args(cargs)
            self.trigger_event("AfterRemoveSource", eargs)
            # triggers are in col row format
            self.trigger_event(f"AfterRemoveSource_{col}_{row}", eargs)
            self._log.debug("remove_source() Leaving.")

    def remove_source_by_calc_cell(self, cell: CalcCell) -> None:
        """
        Removes Source for the cell. This method can used when the cell is being deleted.
        If the cell is not deleted then this method just call ``remove_source()``.

        Args:
            cell (CalcCell): CalcCell object.
        """
        with self._log.indent(True):
            is_deleted = cell.extra_data.get("deleted", False)
            if not is_deleted:
                self.remove_source(cell.cell_obj)
            self._log.debug(f"remove_source_by_calc_cell() - Cell is deleted. {cell.cell_obj}")
            if not "code_name" in cell.extra_data:
                return
            str_id = cell.extra_data["code_name"]
            name = str_id + ".py"
            uri = f"{self._root_uri}/{cell.calc_sheet.unique_id}/{name}"
            if self.sfa.exists(uri):
                self.sfa.delete_file(uri)
                self._log.debug(f"remove_source_by_calc_cell() - Deleted file: {uri}")
            else:
                self._log.debug(f"remove_source_by_calc_cell() - File not found: {uri}")

    def set_global_var(self, name: str, value: Any) -> None:
        """
        Set a global variable in the module.

        Args:
            name (str): Variable name.
            value (Any): Variable value.
        """
        with self._log.indent(True):
            self._log.debug(f"set_global_var() - Setting Global Variable: {name} = {value}")
            self.py_mod.set_global_var(name, value)

    def get_index(self, cell: CellObj) -> int:
        """
        Get index of cell in the data.

        Args:
            cell (CellObj): Cell object.

        Returns:
            int: Index of the cell in the data or ``-1`` if not found.
        """
        with self._log.indent(True):
            try:
                code_cell = self.convert_cell_obj_to_tuple(cell)
                return list(self._data.keys()).index(code_cell)
            except Exception:
                self._log.warning(f"get_index() - Cell {cell} not found.")
                return -1

    # endregion Source Management

    def has_code(self) -> bool:
        """
        Check if the document has any code.

        Returns:
            bool: True if the document has code.
        """
        return len(self) > 0

    def _update_item(self, py_src: PySource) -> bool:
        with self._log.indent(True):
            cargs = CancelEventArgs(self)
            sheet_idx = py_src.sheet_idx
            row = py_src.row
            col = py_src.col
            self._log.debug("_update_item() Entered.")
            self._log.debug(f"_update_item() sheet index: {sheet_idx} col: {col}, row: {row}")
            cargs.event_data = DotDict(
                source=self,
                sheet_idx=sheet_idx,
                row=row,
                col=col,
                code=py_src.source_code,
                doc=self._doc,
                py_src=py_src,
            )
            # triggers are in col row format
            self.trigger_event(f"BeforeSourceUpdate_{col}_{row}", cargs)
            if cargs.cancel:
                return False
            self.trigger_event("BeforeSourceUpdate", cargs)
            if cargs.cancel:
                return False
            code = cargs.event_data.get("code", py_src.source_code)
            if code != py_src.source_code:
                py_src.source_code = code
            # update the dictionary to the current state of the module
            py_src.mod_dict = self.py_mod.mod.__dict__.copy()
            cell_obj = CellObj.from_idx(col_idx=py_src.col, row_idx=py_src.row, sheet_idx=py_src.sheet_idx)
            self.py_mod.set_global_var("CURRENT_CELL_ID", py_src.unique_id)
            self.py_mod.set_global_var("CURRENT_CELL_OBJ", cell_obj)
            result = self.py_mod.update_with_result(py_src.source_code)
            result.py_src = py_src
            py_src.dd_data = result

            eargs = EventArgs.from_args(cargs)
            eargs.event_data["result"] = result
            # triggers are in col row format
            self.trigger_event(f"AfterSourceUpdate_{col}_{row}", eargs)
            self.trigger_event("AfterSourceUpdate", eargs)
            self._log.debug("_update_item() Leaving.")
        return True

    def update_all(self) -> None:
        """
        Rebuilds the module for all the cells.

        Triggers ``BeforeSourceUpdate`` and ``AfterSourceUpdate`` events.
        """
        with self._log.indent(True):
            self._log.debug("update_all() Entered.")
            self.py_mod.reset_module()
            for key in self._data.keys():
                co = CellObj.from_idx(col_idx=key[2], row_idx=key[1], sheet_idx=key[0])
                py_src = self[co]
                self._update_item(py_src)
            self._log.debug("update_all() Leaving.")

    def get_calc_cells(self) -> List[CalcCell]:
        """
        Get all the CalcCells that have code.

        Returns:
            List[CalcCell]: List of CalcCell objects. The order will be Sheet, Row, Column.
        """
        with self._log.indent(True):
            self._log.debug("get_calc_cells() Entered.")
            cc = CellCache(self._doc)
            cells = []
            sheet_idx = -1
            for key in self._data.keys():
                idx, row, col = key
                sheet = None
                if sheet is None or sheet_idx != idx:
                    sheet = self._doc.sheets[idx]
                    sheet_idx = idx
                co = CellObj.from_idx(col_idx=col, row_idx=row, sheet_idx=sheet_idx)
                calc_cell = sheet[co]
                cells.append(calc_cell)
            self._log.debug("get_calc_cells() Leaving.")
            return cells

    def update_from_index(self, index: int) -> None:
        """
        Rebuilds the module from the specified index to the end of the data.

        Args:
            index (int): Index of the cell in the data.

        Returns:
            None:

        Note:
            This method will not update the module for the cell before the specified index.
            This means if the current cell or any cell after has modified a previous cells variable, the module will not be updated correctly.
        """
        with self._log.indent(True):
            self._log.debug(f"update_from_index({index}) Entered.")
            length = len(self)
            if index >= length:
                self._log.warning("update_from_index() Index out of range.")
                return

            if index < 0:
                index = 0
            if index == 0:
                self.update_all()
                return

            # reset the module dictionary to before index item changes
            keys = list(self._data.keys())
            key = keys[index]  # row, col format
            co = CellObj.from_idx(col_idx=key[2], row_idx=key[1], sheet_idx=key[0])
            py_src = self[co]
            if self._is_last_index(index):
                self._log.debug(f"update_from_index({index}). Is last index.")
            else:
                self._log.debug(f"update_from_index({index}). Is not last index. Resetting module to py_src dict.")
                self.py_mod.reset_to_dict(py_src.mod_dict)
            for i in range(index, length):
                key = keys[i]  # tuple in row, col format
                cell_obj = CellObj.from_idx(col_idx=key[2], row_idx=key[1], sheet_idx=key[0])
                py_src = self[cell_obj]
                self._update_item(py_src)
            self._log.debug(f"update_from_index({index}) Leaving.")

    # region Properties

    @property
    def sfa(self) -> Sfa:
        return self._sfa

    @property
    def py_mod(self) -> PyModule:
        return self._mod

    @property
    def log(self) -> OxtLogger:
        return self._log

    # endregion Properties


class PyInstance:
    _instances: Dict[str, PySourceManager] = {}

    def __new__(cls, doc: CalcDoc) -> PySourceManager:
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            # cls._instances[key] = PySourceManager(doc)
            cls._instances[key] = PySourceManager(doc)
            cls._instances[key]._is_init = True
        return cls._instances[key]

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
            inst = cls._instances[key]
            inst.dispose()
            inst = None
            del cls._instances[key]
        else:
            LogInst().debug(f"PyInstance.reset_instance() - Instance not found for doc: {doc.runtime_uid}")


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"doc_{uid}"
    if key in PyInstance._instances:
        del PyInstance._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
