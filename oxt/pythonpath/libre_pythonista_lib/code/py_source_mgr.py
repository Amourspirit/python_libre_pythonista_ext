from __future__ import annotations
from typing import Any, cast, List, Dict, Tuple, TYPE_CHECKING
import types
from pathlib import Path

from sortedcontainers import SortedDict
from ooodev.io.sfa import Sfa
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs


from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
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
        # self._name will be in the format of 'cell_0_0' which is the cell address in column and row
        self._col_row = cast(Tuple[int, int], tuple(map(int, self._name.split("_")[1:])))
        self._src_code = None
        EventsPartial.__init__(self)

        # node.uri = 'vnd.sun.star.tdoc:/1/librepythonista/jymbvnctmujpyb/cell_0_0.py'
        # node.name 'MyFile1'
        # node.provCtx has a sfa (simple file access) object

    def __lt__(self, other: Any):
        # for sort
        if isinstance(other, PySource):
            return self.address < other.address
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
    def address(self) -> Tuple[int, int]:
        """Address in the format of Column an Row. Zero based."""
        return self._col_row

    @property
    def source_code(self) -> str:
        """Gets/Sets the source code from the file. This value is cached after the first call."""
        if self._src_code is None:
            self._src_code = self._get_source()
        return self._src_code

    @source_code.setter
    def source_code(self, code: str) -> None:
        cargs = CancelEventArgs(self)
        cargs.event_data = {"address": self.address, "code": code}
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
    # region Init
    def __init__(self, sheet: CalcSheet) -> None:
        EventsPartial.__init__(self)
        self._sheet = sheet
        self._logger = OxtLogger(log_name=self.__class__.__name__)
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
            result[src.address] = src
        return result

    # endregion Init

    # region Event Subscriptions

    def subscribe_before_source_update(self, cb: EventCallback) -> None:
        self.subscribe_event("BeforeSourceUpdate", cb)

    def subscribe_after_cell_source_update(self, cell: Tuple[int, int], cb: EventCallback) -> None:
        self.subscribe_event(f"AfterSourceUpdate_{cell[0]}_{cell[1]}", cb)

    def subscribe_before_cell_source_update(self, cell: Tuple[int, int], cb: EventCallback) -> None:
        self.subscribe_event(f"BeforeSourceUpdate_{cell[0]}_{cell[1]}", cb)

    def subscribe_after_source_update(self, cb: EventCallback) -> None:
        self.subscribe_event("AfterSourceUpdate", cb)

    def subscribe_before_source_add(self, cb: EventCallback) -> None:
        self.subscribe_event("BeforeSourceAdd", cb)

    def subscribe_after_source_add(self, cb: EventCallback) -> None:
        self.subscribe_event("AfterSourceAdd", cb)

    def subscribe_before_source_remove(self, cb: EventCallback) -> None:
        self.subscribe_event("BeforeSourceRemove", cb)

    def subscribe_after_source_remove(self, cb: EventCallback) -> None:
        self.subscribe_event("AfterSourceRemove", cb)

    def subscribe_before_cell_source_remove(self, cell: Tuple[int, int], cb: EventCallback) -> None:
        self.subscribe_event(f"BeforeSourceRemove_{cell[0]}_{cell[1]}", cb)

    def subscribe_after_cell_source_remove(self, cell: Tuple[int, int], cb: EventCallback) -> None:
        self.subscribe_event(f"AfterSourceRemove_{cell[0]}_{cell[1]}", cb)

    # endregion Event Subscriptions

    # region Dunder Methods

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: Tuple[int, int]) -> PySource:
        return self._data[key]

    def __setitem__(self, key: Tuple[int, int], value: PySource) -> None:
        self._data[key] = value

    def __delitem__(self, key: Tuple[int, int]) -> None:
        self.remove_source(key)

    def __contains__(self, key: Tuple[int, int]) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data.values())

    # endregion Dunder Methods

    # region Source Management

    def add_source(self, code: str, cell: Tuple[int, int]) -> Any:
        if cell in self._data:
            raise Exception(f"Cell {cell} already exists.")
        cargs = CancelEventArgs(self)
        code = cargs.event_data.get("code", code)
        name = f"cell_{cell[0]}_{cell[1]}.py"
        uri = f"{self._root_uri}/{self._sheet.unique_id}/{name}"
        py_src = PySource(uri, self)
        py_src.source_code = code
        self._data[cell] = py_src
        index = self.get_index(cell)
        self._update_from_index(index)

    def update_source(self, code: str, cell: Tuple[int, int]) -> None:
        if cell not in self._data:
            raise Exception(f"Cell {cell} does not exists.")
        cargs = CancelEventArgs(self)
        cargs.event_data = {"address": cell, "code": code}
        self.trigger_event("BeforeSourceUpdate", cargs)
        if cargs.cancel:
            return
        code = cargs.event_data.get("code", code)
        src = self[cell]
        index = self.get_index(cell)
        self._update_from_index(index)
        src.source_code = code
        eargs = EventArgs.from_args(cargs)
        self.trigger_event("AfterSourceUpdate", eargs)
        return None

    def remove_source(self, cell: Tuple[int, int]) -> None:
        if cell not in self._data:
            raise Exception(f"Cell {cell} does not exist.")
        if cell in self._data:
            raise Exception(f"Cell {cell} already exists.")
        cargs = CancelEventArgs(self)
        cargs.event_data = {"address": cell}
        self.trigger_event("BeforeSourceRemove", cargs)
        if cargs.cancel:
            return
        self.trigger_event(f"BeforeSourceRemove_{cell[0]}_{cell[1]}", cargs)
        if cargs.cancel:
            return
        index = self.get_index(cell)
        self._data[cell].del_source()
        del self._data[cell]

        if index == 0 or len(self) == 0:
            self._update_all()
        else:
            self._update_from_index(index - 1)

        eargs = EventArgs.from_args(cargs)
        self.trigger_event("AfterSourceRemove", eargs)
        self.trigger_event(f"AfterSourceRemove_{cell[0]}_{cell[1]}", eargs)

    def get_index(self, cell: Tuple[int, int]) -> int:
        return list(self._data.keys()).index(cell)

    # endregion Source Management

    def _update_item(self, py_src: PySource) -> bool:
        cargs = CancelEventArgs(self)
        cargs.event_data = {"address": py_src.address, "code": py_src.source_code}
        cell = py_src.address
        self.trigger_event("BeforeSourceUpdate", cargs)
        if cargs.cancel:
            return False
        self.trigger_event(f"BeforeSourceUpdate_{cell[0]}_{cell[1]}", cargs)
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
        self.trigger_event("AfterSourceUpdate", eargs)
        self.trigger_event(f"AfterSourceUpdate_{cell[0]}_{cell[1]}", eargs)
        return True

    def _update_all(self) -> None:
        self.py_mod.reset_module()
        for key in self._data.keys():
            py_src = self[key]
            self._update_item(py_src)

    def _update_from_index(self, index: int) -> None:
        length = len(self)
        if index >= length:
            self._logger.warning("_update_from_index() Index out of range.")
            return
        if index < 0:
            index = 0
        if index == 0:
            self._update_all()
            return
        # reset the module dictionary to before index item changes
        keys = list(self._data.keys())
        key = keys[index]
        py_src = self[key]
        self.py_mod.reset_to_dict(py_src.mod_dict)
        for i in range(index, length):
            key = keys[i]  # tuple
            py_src = self[key]
            self._update_item(py_src)

    # region Properties

    @property
    def sfa(self) -> Sfa:
        return self._sfa

    @property
    def py_mod(self) -> PyModule:
        return self._mod

    # endregion Properties
