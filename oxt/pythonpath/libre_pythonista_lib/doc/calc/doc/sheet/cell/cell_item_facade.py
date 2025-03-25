# region Imports
from __future__ import annotations
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind import (
        QryCtlKindFromRuleNameKind,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.code.py_module import PyModule
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from libre_pythonista_lib.cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind import QryCtlKindFromRuleNameKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result

    StateRuleT = Any
    QryHandlerT = Any
    CmdHandlerT = Any

    # endregion Imports

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_cell_item_facade.py


class CellItemFacade(LogMixin):
    """
    Facade pattern implementation for managing cell items in a LibreOffice Calc spreadsheet.
    Handles cell controls, code management, and state rules.
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the facade with a CalcCell instance.

        Args:
            cell: The CalcCell to manage
        """
        LogMixin.__init__(self)
        self._cell = cell
        self._state_rules = StateRules()
        self._py_mod = PyModule()
        self._uri = None
        self._py_src_mgr = PySourceManager(doc=self._cell.calc_doc, mod=self._py_mod)

    def _ensure_code_name(self) -> None:
        """Ensures the cell has a code name set, without overwriting existing ones"""
        cmd = CmdCodeName(cell=self._cell, overwrite_existing=False)
        self.cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to set code name.")

    def _qry_module_state(self) -> ModuleStateItem:
        """Queries the current module state for the cell"""
        qry = QryModuleState(cell=self._cell, mod=self._py_mod)
        result = self.qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _get_uri(self) -> str:
        """Gets the URI for the cell, ensuring it has a code name first"""
        self._ensure_code_name()
        qry = QryCellUri(self._cell)
        result = self.qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def get_control_kind(self) -> CtlKind:
        """Gets the kind of control attached to the cell"""
        qry = QryCtlKind(self._cell)
        result = self.qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        return CtlKind.UNKNOWN

    def add_default_control(self) -> Any:  # noqa: ANN401
        """Adds a default string control to the cell and initializes empty code"""
        _ = ctl_director.create_control(self._cell, CtlKind.STRING)
        self._append_code("")
        try:
            state = self._qry_module_state()
        except Exception:
            self.log.exception("Failed to get module state.")
            return None
        return state.dd_data.get("data")

    def _append_code(self, code: str) -> None:
        """Appends Python code to the cell's module"""
        cmd = CmdAppendCode(cell=self._cell, mod=self._py_mod, code=code)
        self.cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to append code.")

    def get_control(self) -> CtlBase | None:
        """Gets the control object attached to the cell"""
        return ctl_director.get_control(self._cell)

    def remove_control(self) -> bool:
        """Removes any control attached to the cell"""
        return ctl_director.remove_control(self._cell)

    def update_code(self, code: str) -> None:
        """
        Updates the cell's code and adjusts the control type if necessary based on the new code
        """
        current_control = self.get_control()
        if current_control is None:
            self.log.error("update_code() No control found.")
            return
        cmd = CmdUpdateCode(cell=self._cell, mod=self._py_mod, code=code)
        self.cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to update code.")
            return
        rule = self.get_matched_rule()
        if rule is None:
            self.log.error("Failed to get matched rule.")
            return
        rule.rule_kind
        ctl_kind_qry = QryCtlKindFromRuleNameKind(rule.rule_kind)
        ctl_kind = self.qry_handler.handle(ctl_kind_qry)
        if ctl_kind == current_control.control_kind:
            return
        if not self.remove_control():
            self.log.error("Failed to remove control.")
            return
        _ = ctl_director.create_control(self._cell, ctl_kind)

    def get_matched_rule(self) -> StateRuleT | None:
        """Gets the matching state rule for the cell's current state"""
        # do not cache this value. It may change when a cell get updated.
        try:
            state = self._qry_module_state()
        except Exception:
            self.log.exception("Failed to get module state.")
            return None
        return self._state_rules.get_matched_rule(self._cell, state.dd_data)

    def is_control(self) -> bool:
        """Checks if the cell has a control attached"""
        ctl_kind = self.get_control_kind()
        return ctl_kind != CtlKind.UNKNOWN

    def is_source_cell(self) -> bool:
        """Checks if the cell is a source cell"""
        return self.cell.cell_obj in self._py_src_mgr

    def get_value(self) -> Any:  # noqa: ANN401
        """Gets the value of the cell"""
        try:
            state = self._qry_module_state()
        except Exception:
            self.log.exception("Failed to get module state.")
            return None
        result = state.dd_data.get("data", NULL)
        if result is NULL:
            self.log.debug("get_value() No data found. Returning None.")
            return None
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._cell.cell_obj})>"

    @property
    def uri(self) -> str:
        """Gets the cell's URI"""
        if self._uri is None:
            self._uri = self._get_uri()
        return self._uri

    @property
    def py_src_mgr(self) -> PySourceManager:
        """Gets the Python source manager instance"""
        return self._py_src_mgr

    @property
    def py_mod(self) -> PyModule:
        """Gets the Python module instance"""
        return self._py_mod

    @property
    def cell(self) -> CalcCell:
        """Gets the underlying CalcCell instance"""
        return self._cell

    @property
    def cmd_handler(self) -> CmdHandlerT:
        """Gets the command handler from the Python source manager"""
        return self._py_src_mgr.cmd_handler

    @property
    def qry_handler(self) -> QryHandlerT:
        """Gets the query handler from the Python source manager"""
        return self._py_src_mgr.qry_handler
