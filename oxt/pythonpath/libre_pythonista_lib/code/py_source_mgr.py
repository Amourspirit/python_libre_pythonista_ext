from __future__ import annotations
from typing import Any, cast, List, Dict, Tuple, TYPE_CHECKING
import types
from pathlib import Path

from sortedcontainers import SortedDict
from ooodev.io.sfa import Sfa
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.io.log.named_logger import NamedLogger
from ooodev.utils.helper.dot_dict import DotDict

# from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
from .py_module import PyModule

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from ooodev.utils.type_var import EventCallback

_RUN_MOD = cast(types.ModuleType, None)
_MOD_DIR = "librepythonista"


class PySource(EventsPartial):
    def __init__(self, uri: str, mgr: PySourceManager) -> None:
        self._uri = uri
        self._mgr = mgr
        self._mod_dict = mgr.py_mod.mod.__dict__.copy()
        pth = Path(uri)
        self._name = pth.stem
        # self._name will be in the format of 'cell_0_0' which is the cell address in row and column
        # across and then down
        row_col = cast(Tuple[int, int], tuple(map(int, self._name.split("_")[1:])))
        self._row = row_col[0]
        self._col = row_col[1]
        self._src_code = None
        EventsPartial.__init__(self)

        # node.uri = 'vnd.sun.star.tdoc:/1/librepythonista/jymbvnctmujpyb/cell_0_0.py'
        # node.name 'MyFile1'
        # node.provCtx has a sfa (simple file access) object

    def __lt__(self, other: Any):
        # for sort
        if isinstance(other, PySource):
            addr1 = (self.row, self.col)
            addr2 = (other.row, other.col)
            return addr1 < addr2
        return NotImplemented

    def _get_source(self) -> str:
        """Reads the source code from the file. This method does not cache the source code"""
        return self._mgr.sfa.read_text_file(self._uri)

    def _set_source(self, code: str, mode: str = "w") -> None:
        self._mgr.sfa.write_text_file(self._uri, code, mode)

    def del_source(self) -> None:
        self._mgr.sfa.delete_file(self._uri)

    def exit(self) -> bool:
        return self._mgr.sfa.exists(self._uri)

    @property
    def name(self) -> str:
        return self._name

    @property
    def row(self) -> int:
        """Cell row zero based index."""
        return self._row

    @property
    def col(self) -> int:
        """Column zero based index."""
        return self._col

    @property
    def source_code(self) -> str:
        """Gets/Sets the source code from the file. This value is cached after the first call."""
        if self._src_code is None:
            self._src_code = self._get_source()
        return self._src_code

    @source_code.setter
    def source_code(self, code: str) -> None:
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(code=code, row=self.row, col=self.col, sheet=self._mgr._sheet)
        self.trigger_event("BeforeSourceChange", cargs)
        if cargs.cancel:
            return
        code = cargs.event_data.get("code", code)
        self._set_source(code)
        self._src_code = code
        eargs = EventArgs.from_args(cargs)
        self.trigger_event("AfterSourceChange", eargs)

    @property
    def mod_dict(self) -> Dict[str, Any]:
        return self._mod_dict

    @mod_dict.setter
    def mod_dict(self, value: Dict[str, Any]) -> None:
        self._mod_dict = value


class PySourceManager(EventsPartial):
    """
    Python Source code manager.

    Internally data is stored with key in the format of (row, col) and value as PySource object.
    All public facing methods are in the format of (col, row) for cell address because this is how it normally is in Calc.
    """

    # region Init
    def __init__(self, sheet: CalcSheet) -> None:
        EventsPartial.__init__(self)
        self._sheet = sheet
        # self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger = NamedLogger(self.__class__.__name__)
        self._sfa = Sfa()

        self._root_uri = f"vnd.sun.star.tdoc:/{sheet.calc_doc.runtime_uid}/{_MOD_DIR}"
        if not self._sfa.exists(self._root_uri):
            self._sfa.inst.create_folder(self._root_uri)
        self._data = self._get_sources()
        self._mod = PyModule()

    def _get_sources(self) -> SortedDict[Tuple[int, int], PySource]:
        uri = f"{self._root_uri}/{self._sheet.unique_id}"
        if not self._sfa.exists(uri):
            return SortedDict()
        contents = self._sfa.inst.get_folder_contents(uri, False)
        if not contents:
            return SortedDict()
        sources: List[PySource] = []
        for node in contents:
            if node.endswith(".py"):
                sources.append(PySource(node, self))
        sources.sort()
        result = SortedDict()
        for src in sources:
            src.add_event_observers(self.event_observer)
            result[src.row, src.col] = src
        return result

    # endregion Init

    # region Event Subscriptions

    def subscribe_before_source_update(self, cb: EventCallback) -> None:
        """
        Subscribe to before source update event.
        This event is triggered multiple time when a series of cells are being updated.
        This event is triggered after `subscribe_before_cell_source_update``

        Event Args are ``CancelEventArgs``.

        ``event_data`` is a ``DotDict`` with the following keys:

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

    def __getitem__(self, key: Tuple[int, int]) -> PySource:
        """
        Gets an Item

        Args:
            key (Tuple[int, int]): Tuple of Column and Row

        Returns:
            PySource: Source object
        """
        col = key[0]
        row = key[1]
        code_cell = (row, col)
        return self._data[code_cell]

    def __setitem__(self, key: Tuple[int, int], value: PySource) -> None:
        """
        Sets an Item

        Args:
            key (Tuple[int, int]): Tuple of Column and Row
            value (PySource): Source object
        """
        col = key[0]
        row = key[1]
        code_cell = (row, col)
        self._data[code_cell] = value

    def __delitem__(self, key: Tuple[int, int]) -> None:
        """
        Removes an Item

        Args:
            key (Tuple[int, int]): Tuple of Column and Row.
        """
        col = key[0]
        row = key[1]
        code_cell = (row, col)
        self.remove_source(code_cell)

    def __contains__(self, key: Tuple[int, int]) -> bool:
        """
        Checks if key exists in the data.

        Args:
            key (Tuple[int, int]): Tuple of Column and Row

        Returns:
            bool: True if key exists in the data.
        """
        col = key[0]
        row = key[1]
        code_cell = (row, col)
        return code_cell in self._data

    def __iter__(self):
        return iter(self._data.values())

    # endregion Dunder Methods

    # region Source Management

    def add_source(self, code: str, cell: Tuple[int, int]) -> None:
        """
        Add Source code for the cell.

        Args:
            code (str): Source code
            cell (Tuple[int, int]): Cell address in column and row.

        Raises:
            Exception: If cell already exists in current data.
        """
        col = cell[0]
        row = cell[1]
        code_cell = (row, col)

        if code_cell in self._data:
            raise Exception(f"Cell {cell} already exists.")
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(row=row, col=col, code=code, sheet=self._sheet)
        self.trigger_event("BeforeAddSource", cargs)
        if cargs.cancel:
            return
        code = cargs.event_data.get("code", code)
        name = f"cell_{row}_{col}.py"
        uri = f"{self._root_uri}/{self._sheet.unique_id}/{name}"
        py_src = PySource(uri, self)
        py_src.source_code = code
        self._data[code_cell] = py_src
        index = self.get_index(cell)
        self._update_from_index(index)
        eargs = EventArgs.from_args(cargs)
        self.trigger_event("AfterAddSource", eargs)
        return None

    def update_source(self, code: str, cell: Tuple[int, int]) -> None:
        """
        Update the source code for the cell.

        Args:
            code (str): Source code
            cell (Tuple[int, int]): Cell address in row and column.

        Raises:
            Exception: If cell does not exist in current data.
        """
        col = cell[0]
        row = cell[1]
        code_cell = (row, col)
        if code_cell not in self._data:
            raise Exception(f"Cell {cell} does not exists.")
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(row=row, col=col, code=code, sheet=self._sheet)
        self.trigger_event("BeforeUpdateSource", cargs)
        if cargs.cancel:
            return
        code = cargs.event_data.get("code", code)
        src = self[cell]
        index = self.get_index(cell)
        src.source_code = code
        self._update_from_index(index)
        eargs = EventArgs.from_args(cargs)
        self.trigger_event("AfterUpdateSource", eargs)
        return None

    def remove_source(self, cell: Tuple[int, int]) -> None:
        """
        Removes Source for the cell.

        Args:
            cell (Tuple[int, int]): Cell address in row and column.
        """
        col = cell[0]
        row = cell[1]
        code_cell = (row, col)
        if code_cell not in self._data:
            raise Exception(f"Cell {cell} does not exist.")
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(row=row, col=col, sheet=self._sheet)
        self.trigger_event("BeforeRemoveSource", cargs)
        if cargs.cancel:
            return
        # triggers are in col row format
        self.trigger_event(f"BeforeRemoveSource_{col}_{row}", cargs)
        if cargs.cancel:
            return
        index = self.get_index(cell)
        self._data[code_cell].del_source()
        del self._data[code_cell]

        if index == 0 or len(self) == 0:
            self._update_all()
        else:
            self._update_from_index(index - 1)

        eargs = EventArgs.from_args(cargs)
        self.trigger_event("AfterRemoveSource", eargs)
        # triggers are in col row format
        self.trigger_event(f"AfterRemoveSource_{col}_{row}", eargs)

    def get_index(self, cell: Tuple[int, int]) -> int:
        """
        Get index of cell in the data.

        Args:
            cell (Tuple[int, int]): Cell address in Column and Row.

        Returns:
            int: _description_
        """
        code_cell = (cell[1], cell[0])
        return list(self._data.keys()).index(code_cell)

    # endregion Source Management

    def _update_item(self, py_src: PySource) -> bool:
        cargs = CancelEventArgs(self)
        row = py_src.row
        col = py_src.col
        cargs.event_data = DotDict(row=row, col=col, code=py_src.source_code, sheet=self._sheet)
        code_cell = (row, col)
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
        result = self.py_mod.update_with_result(py_src.source_code)

        eargs = EventArgs.from_args(cargs)
        eargs.event_data["result"] = result
        # triggers are in col row format
        self.trigger_event(f"AfterSourceUpdate_{col}_{row}", eargs)
        self.trigger_event("AfterSourceUpdate", eargs)
        return True

    def _update_all(self) -> None:
        self.py_mod.reset_module()
        for key in self._data.keys():
            col_row_key = (key[1], key[0])
            py_src = self[col_row_key]
            self._update_item(py_src)

    def _update_from_index(self, index: int) -> None:
        length = len(self)
        if index >= length:
            self._logger.warning("_update_from_index() Index out of range.")
            return
        if index < length - 1:
            # if index < 0:
            #     index = 0
            # if index == 0:
            self._update_all()
            return

        # reset the module dictionary to before index item changes
        keys = list(self._data.keys())
        key = keys[index]  # row, col format
        col_row_key = (key[1], key[0])
        py_src = self[col_row_key]
        self.py_mod.reset_to_dict(py_src.mod_dict)
        for i in range(index, length):
            key = keys[i]  # tuple in row, col format
            col_row_key = (key[1], key[0])
            py_src = self[col_row_key]
            self._update_item(py_src)

    # region Properties

    @property
    def sfa(self) -> Sfa:
        return self._sfa

    @property
    def py_mod(self) -> PyModule:
        return self._mod

    # endregion Properties
