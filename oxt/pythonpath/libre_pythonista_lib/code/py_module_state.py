from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import GLB_MODULE_SET_GBL_VAR
    from .py_module import PyModule
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.code.py_module import PyModule
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import GLB_MODULE_SET_GBL_VAR

_KEY = "libre_pythonista_lib.code.py_module_state.PyModuleState"


class PyModuleState(LogMixin):
    def __new__(cls) -> PyModuleState:
        gbl_cache = DocGlobals.get_current()
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self.log.debug("Init")
        self._shared_event = SharedEvent()
        self._py_mod = PyModule()
        self._state: Dict[str, Dict[str, Any]] = {}
        self._init_events()
        self._is_init = True

    def __bool__(self) -> bool:
        """Returns True if the dictionary is not empty."""
        return len(self._state) > 0

    def __getitem__(self, cell: CalcCell) -> Dict[str, Any]:
        """Gets item by key using dictionary syntax."""
        return self._state[cell.unique_id]

    def __setitem__(self, cell: CalcCell, value: Dict[str, Any]) -> None:
        """Sets item by key using dictionary syntax."""
        self._state[cell.unique_id] = value

    def __contains__(self, cell: CalcCell) -> bool:
        """Returns True if key exists in dictionary."""
        return cell.unique_id in self._state

    def __len__(self) -> int:
        """Returns the number of items in the dictionary."""
        return len(self._state)

    def _init_events(self) -> None:
        pass
        # self._fn_on_set_global_var = self._on_set_global_var
        # self._shared_event.subscribe_event(GLB_MODULE_SET_GBL_VAR, self._fn_on_set_global_var)

    # region Event Handlers
    # def _on_set_global_var(self, source: Any, event: EventArgs) -> None:  # noqa: ANN401
    #     # triggered in:doc.calc.doc.sheet.cell.code.py_source_manager.PySourceManager.set_global_var
    #     self.log.debug("_on_set_global_var()")
    #     data = cast(DotDict, event.event_data)
    #     props = cast(Dict[str, Any], data.props)
    #     for k, v in props.items():
    #         self.set_global_var(k, v)
    #     self.log.debug("_on_set_global_var() done.")

    # endregion Event Handlers

    def update_with_result(self, cell: CalcCell, code: str = "") -> DotDict[Any]:
        result = self._py_mod.update_with_result(code)
        self._state[cell.unique_id] = self._py_mod.mod.__dict__.copy()
        return result

    def set_global_var(self, var_name: str, value: Any) -> None:  # noqa: ANN401
        self._py_mod.set_global_var(var_name, value)

    def reset_module(self) -> None:
        self._py_mod.reset_module()
        self._state.clear()

    def reset_to_cell(self, cell: CalcCell, code: str = "") -> Any:  # noqa: ANN401
        if not cell in self:
            self.log.debug("Cell %s not found in state.", cell.cell_obj)
            return None
        mod_dict = self[cell]
        result = self._py_mod.reset_to_dict(mod_dict, code)
        self._state.clear()
        return result
