# region Imports
from __future__ import annotations
from typing import Any, Dict, List, Tuple, Iterable, TYPE_CHECKING, cast, Union, Optional
import threading
import time
from sortedcontainers import SortedDict

from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.io.sfa import Sfa
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.string.str_list import StrList


if TYPE_CHECKING:
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.___lo_pip___.debug.py_charm_break_mgr import PyCharmBreakMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_state import PyModuleState
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_del import CmdCellSrcDel
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_cells import QryLpCells
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_py_source import QryCellPySource
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_lp_root_uri import QryLpRootUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_data import PySourceData
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import (
        QryModuleStateLastItem,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.const import (
        PYTHON_BEFORE_ADD_SRC_CODE,
        PYTHON_AFTER_ADD_SRC_CODE,
        PYTHON_BEFORE_UPDATE_SOURCE_CODE,
        PYTHON_AFTER_UPDATE_SOURCE_CODE,
        PYTHON_BEFORE_REMOVE_SOURCE_CODE,
        PYTHON_AFTER_REMOVE_SOURCE_CODE,
        PYTHON_AFTER_SOURCE_UPDATE,
        PYTHON_BEFORE_SOURCE_UPDATE,
        PYTHON_SOURCE_MODIFIED,
    )
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import PY_SRC_MGR_MOD_STATES_INIT_UPDATED
else:
    from ___lo_pip___.debug.break_mgr import BreakMgr
    from ___lo_pip___.debug.py_charm_break_mgr import PyCharmBreakMgr

    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_state import PyModuleState
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_del import CmdCellSrcDel
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_cells import QryLpCells
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_py_source import QryCellPySource
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import QryModuleStateLastItem
    from libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
    from libre_pythonista_lib.cq.qry.doc.qry_lp_root_uri import QryLpRootUri
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_data import PySourceData
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.doc.calc.const import (
        PYTHON_BEFORE_ADD_SRC_CODE,
        PYTHON_AFTER_ADD_SRC_CODE,
        PYTHON_BEFORE_UPDATE_SOURCE_CODE,
        PYTHON_AFTER_UPDATE_SOURCE_CODE,
        PYTHON_BEFORE_REMOVE_SOURCE_CODE,
        PYTHON_AFTER_REMOVE_SOURCE_CODE,
        PYTHON_AFTER_SOURCE_UPDATE,
        PYTHON_BEFORE_SOURCE_UPDATE,
        PYTHON_SOURCE_MODIFIED,
    )
    from libre_pythonista_lib.const.event_const import PY_SRC_MGR_MOD_STATES_INIT_UPDATED

    QryHandlerT = Any
    CmdHandlerT = Any
# endregion Imports

_TREAD_LOCK = threading.Lock()
_THREAD_EVENT = threading.Event()

break_mgr = BreakMgr()  # Initialize the breakpoint manager
break_mgr.add_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager._init_sources")

py_break_mgr = PyCharmBreakMgr()
py_break_mgr.add_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager._init_sources")

_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager.PySourceManager"

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_code/test_py_source_manager.py


class PySourceManager(LogMixin):
    """
    Python Source code manager.

    Internally data is stored with key in the format of (row, col) and value as PySource object.
    All public facing methods are in the format of (col, row) for cell address because this is how it normally is in Calc.
    """

    def __new__(cls, doc: CalcDoc, mod: PyModuleT) -> PySourceManager:
        gbl_cache = DocGlobals.get_current(doc.runtime_uid)
        mod_id = id(mod)
        key = f"{_KEY}_{mod_id}"
        if key in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[key]

        inst = super().__new__(cls)
        inst.cache_key = key
        inst._is_init = False

        gbl_cache.mem_cache[key] = inst
        return inst

    # region Init
    def __init__(self, doc: CalcDoc, mod: PyModuleT) -> None:
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        # don't use CalcDoc.from_current_doc() because there many be multiple documents opened already.
        self.cache_key: str
        self._doc = doc
        self._se = SharedEvent(doc)
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()

        self.log.debug("Init")
        self._sfa = Sfa()
        self._root_uri = self._qry_root_uri()
        self._src_data = cast(SortedDict, None)
        self._mod_state = PyModuleState(mod)
        self._init_sources()
        self._se.trigger_event("PySourceManagerCreated", EventArgs(self))
        self.log.debug("Number of cells in manager: %i", len(self.src_data))
        self.log.debug("Init completed")
        self._is_init = True

    def _init_sources(self) -> None:  # type: ignore
        """Initializes the source code manager."""
        break_mgr.check_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager._init_sources")
        py_break_mgr.check_breakpoint(
            "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager._init_sources"
        )
        self._src_data = SortedDict()
        self._mod_state.reset_module()
        self.log.debug("_init_sources() Entered.")
        sources: List[Tuple[PySource, CalcCell, str]] = []
        code_cells = self._qry_lp_cells()
        for sheet in self._doc.sheets:
            if sheet.sheet_index not in code_cells:
                continue

            cells = code_cells[sheet.sheet_index]
            for cell in cells:
                calc_cell = sheet[cell]
                qry_cell = QryCellUri(calc_cell)
                qry_cell_result = self._qry_handler.handle(qry_cell)
                if Result.is_failure(qry_cell_result):
                    self.log.warning("Failed to get URI for cell %s", cell)
                    continue
                uri = qry_cell_result.data
                py_src = self._qry_py_source(uri=uri, cell=calc_cell)
                sources.append((py_src, calc_cell, uri))

            sources.sort(key=lambda x: x[0])  # Sort by PySource object only.
            self._process_sources(sources)
        self.log.debug("_init_sources() Leaving.")

    def _process_sources(self, sources: List[Tuple[PySource, CalcCell, str]]) -> None:
        _THREAD_EVENT.clear()

        def process_source(calc_cell: CalcCell, code: str, is_last: bool) -> None:
            # This solves a strange issue on Windows.
            #
            # Version: 24.8.6.2 (X86_64) / LibreOffice Community
            # Build ID: 6d98ba145e9a8a39fc57bcc76981d1fb1316c60c
            # CPU threads: 4; OS: Windows 10 X86_64 (10.0 build 19045); UI render: Skia/Raster; VCL: win
            # Locale: en-US (en_US); UI: en-US
            # Calc: CL threaded
            #
            # It is not absolutely clear on what the issue is. LibreOffice Calc was crashing when a sheet was loaded that contained a matplotlib plot.
            # The crash was a complete crash and did not give any usable info in the log files to trace.
            # Debugging was able to trace the code to the point:
            #
            # C:\Users\bigby\AppData\Roaming\Python\Python39\64\site-packages\matplotlib\transforms.py
            # Line 881
            # points, minpos, changed = update_path_extents(path, None, self._points, self._minpos, ignore)

            # update_path_extents in a method in binary file _path.cp39-win_amd64.pyd
            # in C:\Users\bigby\AppData\Roaming\Python\Python39\64\site-packages\matplotlib
            #
            # If self._mod_state.update_with_result(cell=calc_cell, code=code) is call on the main
            # thread then the crash would occur. If it is called on a separate thread then the crash does not occur.
            # When called on a separate thread there is thenot real value because the main thread continues.
            # Calling Join just causes the thread to hang.
            # After the last source is processed the event is set and the main thread continues.
            # The event calls a method that then calls the sheet caculateAll method.
            # From this point forward all seems to work fine. on all systems.
            # In theory I could have applied this to windows only but it works fine on other os'es as well.
            # See: libre_pythonista_lib.doc.calc.doc.doc_event_mgr.DocEventMgr
            # see: libre_pythonista_lib.doc.calc.doc.lp_listeners.listener_py_src_mgr_mod_states_init_updated.ListenerPySrcMgrModStatesInitUpdated

            with _TREAD_LOCK:
                time.sleep(0.1)
                # _ = self._mod_state.update_with_result(cell=calc_cell, code=code)
            if is_last:
                # self.log.debug("Last source processed.")
                self._se.trigger_event(PY_SRC_MGR_MOD_STATES_INIT_UPDATED, EventArgs(self))
                _THREAD_EVENT.set()

        threads = []
        count = len(sources)
        for i, src in enumerate(sources):
            is_last = i + 1 == count
            py_src = src[0]
            calc_cell = src[1]
            uri = src[2]
            self.src_data[py_src.sheet_idx, py_src.row, py_src.col] = PySourceData(
                uri=uri, cell=calc_cell.cell_obj.copy()
            )
            self.set_global_var("CURRENT_CELL_ID", py_src.uri_info.unique_id)
            self.set_global_var("CURRENT_CELL_OBJ", calc_cell.cell_obj)
            # _ = self._mod_state.update_with_result(cell=calc_cell, code=py_src.source_code)
            process_thread = threading.Thread(
                target=process_source, args=(calc_cell, py_src.source_code, is_last), daemon=True
            )
            threads.append(process_thread)
            process_thread.start()

        return

        # wait 5 seconds to see if threads are complete
        start_time = time.time()
        while not _THREAD_EVENT.is_set():
            if time.time() - start_time > 5:
                break
            time.sleep(0.1)

        # for thread in threads:
        #     thread.join()

    # endregion Init

    # region Qry Methods

    def _qry_root_uri(self) -> str:
        qry = QryLpRootUri(doc=self._doc)
        return self._qry_handler.handle(qry)

    def _qry_lp_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        qry = QryLpCells(doc=self._doc)
        return self._qry_handler.handle(qry)

    def _qry_cell_cp_code_name(self) -> str:
        """
        Query class that retrieves the codename from configuration.
        Something like ``libre_pythonista_codename``
        """
        qry = QryCellCpCodeName()
        return self._qry_handler.handle(qry)

    def _qry_cell_uri(self, cell: CalcCell) -> str:
        qry = QryCellUri(cell=cell)
        result = self._qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_py_source(self, uri: str, cell: CalcCell) -> PySource:
        qry = QryCellPySource(uri=uri, cell=cell)
        return self._qry_handler.handle(qry)

    def qry_last_module_state_item(self) -> Union[ModuleStateItem, None]:
        """Returns the last module state item or None if empty."""
        qry = QryModuleStateLastItem(mod=self._mod_state.mod)
        result = self._qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        return None

    def qry_module_state_item(self, cell: CalcCell) -> Union[ModuleStateItem, None]:
        """Returns the last module state item or None if empty."""
        qry = QryModuleState(cell=cell, mod=self.mod)
        result = self._qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        return None

    # endregion Qry Methods

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
        self._se = cast(SharedEvent, None)

    def get_module_source_code(self, max_cell: Optional[CellObj] = None, include_max: bool = True) -> str:
        """
        Gets a string that represents the source code of the modules current state.

        If max_cell is specified, the source code will be generated up to the max_cell.

        Args:
            max_cell (CellObj, optional): Maximum cell address. Defaults to None.
            include_max (bool, optional): Include the max cell in the source code. Defaults to True.
        """
        sb = StrList(sep="\n")
        sb.append(f"# Source code for doc: vnd.sun.star.tdoc:/{self._doc.runtime_uid}/")
        for py_src_data in self.src_data.values():
            py_src = PySource(uri=py_src_data.uri, cell=py_src_data.cell)
            cell_obj = CellObj.from_idx(col_idx=py_src.col, row_idx=py_src.row, sheet_idx=py_src.sheet_idx)
            if max_cell is not None:
                if include_max:
                    if cell_obj > max_cell:
                        break
                else:
                    if cell_obj >= max_cell:
                        break

            sb.append(f"# Code for Cell: {cell_obj} of sheet index: {cell_obj.sheet_idx}")
            sb.append(py_src.source_code)
            sb.append()
        return str(sb)

    def dump_module_source_code_to_log(self) -> str:
        """
        Dumps the module source code to the log.

        Returns the current source code.
        """
        src_code = self.get_module_source_code()
        self.log.debug(
            "dump_module_source_code_to_log() - Module Source Code:\n# Start Dump\n%s\n\n# End Dump", src_code
        )
        return src_code

    def _getitem_py_src_data(self, key: Union[CellObj, Tuple[int, int, int]]) -> PySourceData:
        """
        Gets an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of Sheet, Column and Row

        Returns:
            PySourceData: Source object
        """
        is_db = self.log.is_debug
        code_cell = self.convert_cell_obj_to_tuple(key) if isinstance(key, CellObj) else key
        if is_db:
            self.log.debug("__getitem__() - Code Cell: %s", code_cell)
        py_data = cast(PySourceData, self.src_data[code_cell])
        return py_data

    # region Dunder Methods

    def __len__(self) -> int:
        return len(self.src_data)

    def __getitem__(self, key: Union[CellObj, Tuple[int, int, int]]) -> PySource:
        """
        Gets an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of Sheet, Column and Row

        Returns:
            PySource: Source object
        """
        py_data = self._getitem_py_src_data(key)
        result = PySource(uri=py_data.uri, cell=py_data.cell)
        self.log.debug("__getitem__() - Result Unique Id: %s", result.uri_info.unique_id)
        return result

    def __setitem__(self, key: Union[CellObj, Tuple[int, int, int]], value: Union[PySource, PySourceData]) -> None:
        """
        Sets an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of sheet, Column and Row
            value (PySource, PySourceData): Source object
        """
        code_cell = self.convert_cell_obj_to_tuple(key) if isinstance(key, CellObj) else key
        if isinstance(value, PySource):
            value = PySourceData(uri=value.uri, cell=value.cell_obj.copy())
        self.src_data[code_cell] = value
        eargs = EventArgs(self)
        eargs.event_data = DotDict(source=self, value=value, cell_obj=value.cell.copy(), sheet_idx=code_cell[0])
        self._se.trigger_event(PYTHON_SOURCE_MODIFIED, eargs)

    def __delitem__(self, key: Union[CellObj, Tuple[int, int, int]]) -> None:
        """
        Removes an Item

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of sheet, Column and Row
        """
        co = key if isinstance(key, CellObj) else self.convert_tuple_to_cell_obj(key)
        self.remove_source(co)

    def __contains__(self, key: Union[CellObj, Tuple[int, int, int]]) -> bool:
        """
        Checks if key exists in the data.

        Args:
            key (CellObj, Tuple[int, int]): CellObj or Tuple of sheet, Column and Row

        Returns:
            bool: True if key exists in the data.
        """
        code_cell = self.convert_cell_obj_to_tuple(key) if isinstance(key, CellObj) else key
        return code_cell in self.src_data

    def __iter__(self):  # noqa: ANN204
        # return iterable of PySource objects
        for key in self.src_data:
            key: Tuple[int, int, int]
            py_data = self._getitem_py_src_data(key)
            yield PySource(uri=py_data.uri, cell=py_data.cell)

    def py_src_date_items(self) -> Iterable[PySourceData]:
        """Returns an iterable of PySourceData objects."""
        for key in self.src_data:
            key: Tuple[int, int, int]
            yield self.src_data[key]

    # endregion Dunder Methods

    def _is_last_index(self, index: int) -> bool:
        """Checks if index is the last index."""
        return index == len(self) - 1

    def _get_first_item(self) -> Union[PySourceData, None]:
        """Returns the first item in the source manager or None if empty."""
        # get the first item in self._data
        if len(self) == 0:
            return None
        py_data = self._getitem_py_src_data(list(self.src_data.keys())[0])
        return py_data

    def get_first_item(self) -> Union[PySource, None]:
        """Returns the first item in the source manager or None if empty."""
        py_data = self._get_first_item()
        if py_data is None:
            return None
        return PySource(uri=py_data.uri, cell=py_data.cell)

    def _get_last_item(self) -> Union[PySourceData, None]:
        """Returns the last item in the source manager or None if empty."""
        # get the last item in self._data
        if len(self) == 0:
            return None

        py_data = self._getitem_py_src_data(list(self.src_data.keys())[-1])
        return py_data

    def get_next_item_py_src_data(self, cell: CellObj, require_exist: bool = False) -> Union[PySourceData, None]:
        """
        Returns the next item in the source manager or None if empty.

        Args:
            cell (CellObj): Cell object.
            require_exist (bool, optional): If True, the cell must exist in the source manager. Defaults to False.

        Returns:
            PySourceData, None: Source data or None if not found.
        """
        if len(self) == 0:
            self.log.debug("get_next_item_py_src_data() - No items in source manager.")
            return None
        index = self.get_index(cell)
        if require_exist and index < 0:
            self.log.debug("get_next_item_py_src_data() - Cell %s not found.", cell)
            return None
        if index == len(self) - 1:
            return None
        if index > 0:
            self.log.debug("get_next_item_py_src_data() - Cell %s is the next item.", cell)
            py_data = cast(PySourceData, self[list(self.src_data.keys())[index + 1]])
            return py_data
        # negative index means the cell is not in this instance.
        found = None
        for key in self.src_data:
            itm = cast(PySourceData, self.src_data[key])
            if self.log.is_debug:
                self.log.debug(
                    "get_next_item_py_src_data() - Item cell %s > cell %s is %s", itm.cell, cell, itm.cell > cell
                )
            if itm.cell > cell:
                found = itm
                break
        if found is None:
            self.log.debug("get_next_item_py_src_data() - Cell %s not found.", cell)
        else:
            self.log.debug("get_next_item_py_src_data() - Found cell %s after current cell %s.", found.cell, cell)
        return found

    def get_next_item(self, cell: CellObj, require_exist: bool = False) -> Union[PySource, None]:
        """
        Returns the next item in the source manager or None if empty.

        Args:
            cell (CellObj): Cell object.
            require_exist (bool, optional): If True, the cell must exist in the source manager. Defaults to False.

        Returns:
            PySource, None: Source data or None if not found.
        """
        py_data = self.get_next_item_py_src_data(cell=cell, require_exist=require_exist)
        if py_data is None:
            return None
        return PySource(uri=py_data.uri, cell=py_data.cell)

    def get_prev_item_py_src_data(self, cell: CellObj, require_exist: bool = False) -> Union[PySourceData, None]:
        """
        Returns the previous item in the source manager or None if empty.

        Args:
            cell (CellObj): Cell object.
            require_exist (bool, optional): If True, the cell must exist in the source manager. Defaults to False.

        Returns:
            PySourceDat, None: Source data or None if not found.
        """
        if len(self) == 0:
            self.log.debug("get_prev_item_py_src_data() - No items in source manager.")
            return None
        index = self.get_index(cell)
        if require_exist and index < 0:
            self.log.debug("get_prev_item_py_src_data() - Cell %s not found and require_exist is True.", cell)
            return None
        if index == 0:
            self.log.debug("get_prev_item_py_src_data() - Cell %s is the first item.", cell)
            return None
        if index > 0:
            self.log.debug("get_prev_item_py_src_data() - Cell %s is the previous item.", cell)
            py_data = cast(PySourceData, self[list(self.src_data.keys())[index - 1]])
            return py_data
        # negative index means the cell is not in this instance.
        found = None
        for key in reversed(self.src_data):
            itm = cast(PySourceData, self.src_data[key])
            if self.log.is_debug:
                self.log.debug(
                    "get_prev_item_py_src_data() - Item cell %s < cell %s is %s", itm.cell, cell, itm.cell < cell
                )
            if itm.cell < cell:
                found = itm
                break
        if found is None:
            self.log.debug("get_prev_item_py_src_data() - Cell %s not found.", cell)
        else:
            self.log.debug("get_prev_item_py_src_data() - Found cell %s before current cell %s.", found.cell, cell)
        return found

    def get_prev_item(self, cell: CellObj, require_exist: bool = False) -> Union[PySource, None]:
        """
        Returns the previous item in the source manager or None if empty.

        Args:
            cell (CellObj): Cell object.
            require_exist (bool, optional): If True, the cell must exist in the source manager. Defaults to False.

        Returns:
            PySource, None: Source data or None if not found.
        """
        py_data = self.get_prev_item_py_src_data(cell=cell, require_exist=require_exist)
        if py_data is None:
            return None
        return PySource(uri=py_data.uri, cell=py_data.cell)

    def get_last_item(self) -> Union[PySource, None]:
        """Returns the last item in the source manager or None if empty."""
        py_data = self._get_last_item()
        if py_data is None:
            return None
        return PySource(uri=py_data.uri, cell=py_data.cell)

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

    def convert_cell_obj_to_calc_cell(self, cell: CellObj) -> CalcCell:
        """
        Converts a cell object to a CalcCell object.

        Args:
            cell (CellObj): Cell object.

        Returns:
            CalcCell: CalcCell object.
        """
        sheet_idx = cell.sheet_idx
        sheet = self._doc.sheets[sheet_idx]
        return sheet[cell]

    def update_key(self, old_cell: CellObj, new_cell: CellObj) -> None:
        """
        Updates the key for a cell.

        Args:
            old_cell (CellObj): Old cell object.
            new_cell (CellObj): New cell object.
        """
        self.log.debug("update_key() - Updating key for cell %s to %s", old_cell, new_cell)
        old_key = self.convert_cell_obj_to_tuple(old_cell)
        new_key = self.convert_cell_obj_to_tuple(new_cell)
        # if self.log.is_debug:
        #     self.log.debug(self._data.keys())
        if old_key not in self:
            self.log.warning("update_key() - Old key not found: %s", old_key)
            return

        # try:
        #     sheet = self._doc.sheets[old_cell.sheet_idx]
        #     calc_cell = sheet[new_cell]
        #     uri = self._qry_cell_uri(calc_cell)
        # except Exception:
        #     self.log.error("update_key() - Failed to get URI.")
        #     return
        old_data = cast(PySourceData, self.src_data.pop(old_key))
        # if self.log.is_debug:
        #     self.log.debug("old URI: %s", old_data.uri)
        #     self.log.debug("new URI: %s", uri)
        new_data = PySourceData(uri=old_data.uri, cell=new_cell.copy())
        self.src_data[new_key] = new_data
        self._mod_state.update_key(old_cell, new_cell)
        self.log.debug("update_key() - Updated key for cell %s to %s", old_cell, new_cell)

    # region Source Management

    def add_source(self, code: str, cell_obj: CellObj) -> None:
        """
        Add Source code for the cell.

        Args:
            code (str): Source code
            cell_obj (CellObj): Cell object.

        Raises:
            Exception: If cell already exists in current data.
        """
        self.log.debug("add_source() - Adding Source")

        # when adding source is should update the whole module unless it is the last cell for the module.
        cell = self.convert_cell_obj_to_calc_cell(cell_obj)
        code_cell = self.convert_cell_obj_to_tuple(cell_obj)
        sheet_idx = code_cell[0]
        row = code_cell[1]
        col = code_cell[2]
        self.log.debug("add_source() sheet index: %i col: %i, row: %i", sheet_idx, col, row)
        if code_cell in self.src_data:
            self.log.error("add_source() - Cell %s already exists.", cell_obj)
            raise Exception(f"Cell {cell_obj} already exists.")
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(
            source=self,
            sheet_idx=sheet_idx,
            cell=cell,
            row=row,
            col=col,
            code=code,
            doc=self._doc,
        )
        self._se.trigger_event(PYTHON_BEFORE_ADD_SRC_CODE, cargs)
        if cargs.cancel:
            return
        code = cargs.event_data.get("code", code)

        cmd_code_name = CmdCodeName(cell=cell, overwrite_existing=False)
        self._cmd_handler.handle(cmd_code_name)
        if not cmd_code_name.success:
            self.log.error("add_source() - Failed to set code name.")
            return

        try:
            uri = self._qry_cell_uri(cell)
        except Exception:
            self.log.error("add_source() - Failed to get URI.")
            return

        cmd_src_code = CmdCellSrcCode(uri=uri, cell=cell, code=code)

        self._cmd_handler.handle(cmd_src_code)
        if not cmd_src_code.success:
            self.log.error("add_source() - Failed to set code name.")
            return

        sheet = self._doc.sheets[sheet_idx]
        calc_cell = sheet[cell_obj]

        py_src = self._qry_py_source(uri=uri, cell=calc_cell)

        self.src_data[code_cell] = PySourceData(uri=uri, cell=calc_cell.cell_obj.copy())
        index = self.get_index(cell_obj)
        if index < 0:
            self.log.error("add_source() - Cell %s not found.", cell_obj)
            raise Exception(f"Cell {cell_obj} not found.")
        if self._is_last_index(index):
            self.log.debug("add_source() - Last Index, updating from index %i", index)
            self.update_from_index(index)
        else:
            self.log.debug("add_source() not last index, Updating all")
            self.update_all()
        eargs = EventArgs.from_args(cargs)
        eargs.event_data.code_name = py_src.uri_info.unique_id

        self._se.trigger_event(PYTHON_AFTER_ADD_SRC_CODE, eargs)
        # see: doc.calc.doc.sheet.cell.code.cell_cache.CellCache.on_python_src_code_inserted()
        self.log.debug("Done Adding Source")
        return None

    def update_source(self, code: str, cell_obj: CellObj) -> None:
        """
        Update the source code for the cell.

        Args:
            code (str): Source code
            cell (Tuple[int, int]): Cell address in row and column.

        Raises:
            Exception: If cell does not exist in current data.
        """
        self.log.debug("update_source()")
        # when updating source is should update the whole module unless it is the last cell for the module.
        code_cell = self.convert_cell_obj_to_tuple(cell_obj)
        sheet_idx = code_cell[0]
        row = code_cell[1]
        col = code_cell[2]
        self.log.debug("update_source() sheet index: %i col: %i, row: %i", sheet_idx, col, row)

        if code_cell not in self.src_data:
            raise Exception(f"Cell {cell_obj} does not exists.")
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(
            source=self,
            sheet_idx=sheet_idx,
            row=row,
            col=col,
            code=code,
            doc=self._doc,
        )
        self._se.trigger_event(PYTHON_BEFORE_UPDATE_SOURCE_CODE, cargs)
        if cargs.cancel:
            return
        code = cargs.event_data.get("code", code)
        src = self[cell_obj]
        index = self.get_index(cell_obj)
        if index < 0:
            self.log.error("update_source() - Cell %s not found.", cell_obj)
            raise Exception(f"Cell {cell_obj} not found.")
        src.source_code = code  # writes code to file
        # CellCache.reset_instance()

        if self._is_last_index(index):
            self.log.debug("update_source() is last index updating from index %i", index)
            self.update_from_index(index)
        else:
            self.log.debug("update_source() not last index, Updating all")
            self.update_all()
        eargs = EventArgs.from_args(cargs)
        self._se.trigger_event(PYTHON_AFTER_UPDATE_SOURCE_CODE, eargs)
        return None

    def remove_source(self, cell_obj: CellObj) -> None:
        """
        Removes Source for the cell.

        - Deletes the source code.
        - Removes cell from PySourceManager instance.
        - Removes the custom property from the cell.
        - Updates the module to reflect the changes.

        Args:
            cell_obj (CellObj): Cell object.
        """
        # when removing even if this was the last cell, the module should be reset.
        # It is possible that the cell that is being removed contained code that modified a previous cell.
        # _update_from_index() will not restore the values of cells that were modified by the cell being removed.
        cell = self.convert_cell_obj_to_calc_cell(cell_obj)
        self.log.debug("remove_source() Entered.")
        code_cell = self.convert_cell_obj_to_tuple(cell_obj)
        sheet_idx = code_cell[0]
        row = code_cell[1]
        col = code_cell[2]
        self.log.debug("remove_source() sheet index: %i col: %i, row: %i", sheet_idx, col, row)

        if code_cell not in self.src_data:
            raise Exception(f"Cell {cell_obj} does not exist.")
        cargs = CancelEventArgs(self)
        cargs.event_data = DotDict(
            source=self, sheet_idx=sheet_idx, cell=cell, row=row, col=col, doc=self._doc, cell_obj=cell_obj.copy()
        )
        self._se.trigger_event(PYTHON_BEFORE_REMOVE_SOURCE_CODE, cargs)
        if cargs.cancel:
            return
        # triggers are in col row format
        self._se.trigger_event(f"{PYTHON_BEFORE_REMOVE_SOURCE_CODE}_{col}_{row}", cargs)
        if cargs.cancel:
            return
        self[code_cell].del_source()
        del self.src_data[code_cell]
        sheet = self._doc.sheets[sheet_idx]
        calc_cell = sheet[cell_obj]

        cmd_del = CmdCodeNameDel(cell=calc_cell)
        self._cmd_handler.handle(cmd_del)
        if not cmd_del.success:
            # not critical if fail.
            self.log.debug("remove_source() - Failed to delete code name.")

        self.log.debug("remove_source() Calling update_all()")
        self.update_all()

        eargs = EventArgs.from_args(cargs)
        self._se.trigger_event(PYTHON_AFTER_REMOVE_SOURCE_CODE, eargs)
        # triggers are in col row format
        self._se.trigger_event(f"{PYTHON_AFTER_REMOVE_SOURCE_CODE}_{col}_{row}", eargs)

        self._se.trigger_event(PYTHON_SOURCE_MODIFIED, eargs)

        self.log.debug("remove_source() Leaving.")

    def remove_source_by_calc_cell(self, cell: CalcCell) -> None:
        """
        Removes Source for the cell. This method can used when the cell has been deleted.
        If the cell is not deleted then this method just calls ``remove_source()``.

        - Deletes the source code.
        - Removes cell from CellCache.
        - Removes the custom property from the cell.
        - Updates the module to reflect the changes.

        Args:
            cell (CalcCell): CalcCell object.
        """

        qry_deleted = QryCellIsDeleted(cell=cell)
        is_deleted = self._qry_handler.handle(qry_deleted)

        # is_deleted = cell.extra_data.get("deleted", False)

        if not is_deleted:
            self.remove_source(cell.cell_obj)

        cmd_del = CmdCellSrcDel(cell=cell)
        self._cmd_handler.handle(cmd_del)
        if cmd_del.success:
            self.log.debug("remove_source_by_calc_cell() - Successfully executed command.")
        else:
            self.log.error("remove_source_by_calc_cell() - Failed to execute command.")

    def remove_last(self) -> None:
        """Removes the source for the last item in the source manager."""
        if len(self) == 0:
            return
        cell_obj = self.convert_tuple_to_cell_obj(list(self.src_data.keys())[-1])
        self.remove_source(cell_obj)

    def set_global_var(self, name: str, value: Any) -> None:  # noqa: ANN401
        """
        Set a global variable in the module.

        Args:
            name (str): Variable name.
            value (Any): Variable value.
        """
        self._mod_state.set_global_var(name, value)

    def get_index(self, cell: CellObj) -> int:
        """
        Get index of cell in the data.

        Args:
            cell (CellObj): Cell object.

        Returns:
            int: Index of the cell in the data or ``-1`` if not found.
        """
        try:
            code_cell = self.convert_cell_obj_to_tuple(cell)
            return list(self.src_data.keys()).index(code_cell)
        except Exception:
            self.log.debug("get_index() - Cell %s not found.", cell)
            return -1

    # endregion Source Management

    def has_code(self) -> bool:
        """
        Check if the document has any code.

        Returns:
            bool: True if the document has code.
        """
        return len(self) > 0

    def _update_item(self, py_src: Union[PySource, PySourceData]) -> bool:
        if isinstance(py_src, PySourceData):
            py_src = PySource(uri=py_src.uri, cell=py_src.cell)
        cargs = CancelEventArgs(self)
        sheet_idx = py_src.sheet_idx
        row = py_src.row
        col = py_src.col
        sheet = self._doc.sheets[sheet_idx]
        cell_obj = CellObj.from_idx(col_idx=col, row_idx=row, sheet_idx=sheet_idx)
        calc_cell = sheet[cell_obj]

        self.log.debug("_update_item() Entered.")
        self.log.debug("_update_item() sheet index: %i col: %i, row: %i", sheet_idx, col, row)
        src_code = py_src.source_code
        cargs.event_data = DotDict(
            source=self,
            sheet_idx=sheet_idx,
            row=row,
            col=col,
            code=src_code,
            doc=self._doc,
            py_src=py_src,
            cell_obj=cell_obj.copy(),
        )
        # triggers are in col row format
        self._se.trigger_event(f"{PYTHON_BEFORE_SOURCE_UPDATE}_{col}_{row}", cargs)
        if cargs.cancel:
            return False
        self._se.trigger_event(PYTHON_BEFORE_SOURCE_UPDATE, cargs)
        if cargs.cancel:
            return False
        code = cargs.event_data.get("code", src_code)
        if code != src_code:
            py_src.source_code = code  # writes code to file
        # update the dictionary to the current state of the module

        self.set_global_var("CURRENT_CELL_ID", py_src.uri_info.unique_id)
        self.set_global_var("CURRENT_CELL_OBJ", cell_obj)

        try:
            result = self._mod_state.update_with_result(calc_cell, py_src.source_code)
            result.py_src = py_src
        except Exception as e:
            self.log.exception("_update_item() - Error updating module. %s", e)
            return False

        eargs = EventArgs.from_args(cargs)
        eargs.event_data["result"] = result
        # triggers are in col row format
        self._se.trigger_event(f"{PYTHON_AFTER_SOURCE_UPDATE}_{col}_{row}", eargs)
        self._se.trigger_event(PYTHON_SOURCE_MODIFIED, eargs)
        self.log.debug("_update_item() Leaving.")
        return True

    def update_all(self) -> None:
        """
        Rebuilds the module for all the cells.

        Triggers ``BeforeSourceUpdate`` and ``AfterSourceUpdate`` events.
        """
        self.log.debug("update_all() Entered.")
        self._mod_state.reset_module()
        for key in self.src_data:
            co = CellObj.from_idx(col_idx=key[2], row_idx=key[1], sheet_idx=key[0])
            py_src_data = self._getitem_py_src_data(co)
            self._update_item(py_src_data)
        self.log.debug("update_all() Leaving.")

    def get_calc_cells(self) -> List[CalcCell]:
        """
        Get all the CalcCells that have code.

        Returns:
            List[CalcCell]: List of CalcCell objects. The order will be Sheet, Row, Column.
        """
        self.log.debug("get_calc_cells() Entered.")
        cells = []
        sheet_idx = -1
        for key in self.src_data:
            idx, row, col = key
            sheet = None
            if sheet is None or sheet_idx != idx:
                sheet = self._doc.sheets[idx]
                sheet_idx = idx
            co = CellObj.from_idx(col_idx=col, row_idx=row, sheet_idx=sheet_idx)
            calc_cell = sheet[co]
            cells.append(calc_cell)
        self.log.debug("get_calc_cells() Leaving.")
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
        self.log.debug("update_from_index(%i) Entered.", index)
        length = len(self)
        if index >= length:
            self.log.warning("update_from_index() Index out of range.")
            return

        if index < 0:
            index = 0
        if index == 0:
            self.update_all()
            return

        # reset the module dictionary to before index item changes
        keys = list(self.src_data.keys())
        key = keys[index]  # row, col format
        co = CellObj.from_idx(col_idx=key[2], row_idx=key[1], sheet_idx=key[0])
        # py_src = self[co]
        if self._is_last_index(index):
            self.log.debug("update_from_index(%i). Is last index.", index)
        else:
            self.log.debug("update_from_index(%i). Is not last index. Resetting module to py_src dict.", index)
            calc_cell = self.convert_cell_obj_to_calc_cell(co)
            self._mod_state.rollback_to_state(calc_cell)
        for i in range(index, length):
            key = keys[i]  # tuple in row, col format
            cell_obj = CellObj.from_idx(col_idx=key[2], row_idx=key[1], sheet_idx=key[0])
            py_src_data = self._getitem_py_src_data(cell_obj)
            self._update_item(py_src_data)
        self.log.debug("update_from_index(%i) Leaving.", index)

    # region Cache
    def clear_instance_cache(self) -> None:
        """
        Clears the instance cache.
        """
        gbl_cache = DocGlobals.get_current()

        if self.cache_key in gbl_cache.mem_cache:
            del gbl_cache.mem_cache[self.cache_key]
            self.log.debug("clear_instance_cache() - Cleared instance cache.")

        self._mod_state.clear_instance_cache()

    # endregion Cache

    # region Properties

    @property
    def sfa(self) -> Sfa:
        return self._sfa

    @property
    def state_history(self) -> PyModuleState:
        return self._mod_state

    @property
    def mod(self) -> PyModuleT:
        return self._mod_state.mod

    @property
    def doc(self) -> CalcDoc:
        return self._doc

    @property
    def cmd_handler(self) -> CmdHandlerT:
        return self._cmd_handler

    @property
    def qry_handler(self) -> QryHandlerT:
        return self._qry_handler

    @property
    def src_data(self) -> SortedDict:
        if self._src_data is None:
            self._init_sources()
        return self._src_data

    # endregion Properties
