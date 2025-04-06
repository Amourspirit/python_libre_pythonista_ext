# region Imports
from __future__ import annotations
from typing import Any, Iterable, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code import QryCellSrcCode
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_value import QryValue
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_state_rules_default import (
        QryStateRulesDefault,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind import (
        QryCtlKindFromRuleNameKind,
    )

else:
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.code.py_module import PyModule
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from libre_pythonista_lib.cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind import QryCtlKindFromRuleNameKind
    from libre_pythonista_lib.cq.qry.calc.doc.qry_init_calculate import QryInitCalculate
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code import QryCellSrcCode
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_value import QryValue
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_state_rules_default import QryStateRulesDefault
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
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
        self._py_mod = PyModule()
        self._uri = None
        self._py_src_mgr = PySourceManager(doc=self._cell.calc_doc, mod=self._py_mod)
        self._cache = {}
        self._doc_init = None
        self._init_calculate = None
        self.log.debug("CellItemFacade.__init__() for cell: %s", self._cell.cell_obj)

    def _ensure_code_name(self) -> None:
        """Ensures the cell has a code name set, without overwriting existing ones"""
        cmd = CmdCodeName(cell=self._cell, overwrite_existing=False)
        self.cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to set code name.")

    def _qry_init_calculate(self) -> bool:
        """Queries if the document has been initialized for calculation"""
        qry = QryInitCalculate(uid=self._cell.calc_doc.runtime_uid)
        return self.qry_handler.handle(qry)

    def _qry_state_rules(self) -> StateRules:
        """Queries the default state rules for the cell"""
        # QryStateRulesDefault is a cached query
        qry = QryStateRulesDefault()
        return self.qry_handler.handle(qry)

    def _qry_module_state(self) -> ModuleStateItem:
        """Queries the current module state for the cell"""
        key = "qry_module_state_result"
        if key in self._cache:
            result = self._cache[key]
        else:
            qry = QryModuleState(cell=self._cell, mod=self._py_mod)
            result = self.qry_handler.handle(qry)
            self._cache[key] = result
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_uri(self) -> str:
        """Gets the URI for the cell, ensuring it has a code name first"""
        key = "qry_uri_result"
        if key in self._cache:
            result = self._cache[key]
        else:
            self._ensure_code_name()
            qry = QryCellUri(self._cell)
            result = self.qry_handler.handle(qry)
            self._cache[key] = result
        if Result.is_success(result):
            self.log.debug("qry_uri_result: %s", result.data)
            return result.data
        raise result.error

    def _qry_src_code(self) -> str:
        qry = QryCellSrcCode(cell=self._cell, uri=self.uri)
        result = self.qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_ctl_rule_name_kind(self) -> RuleNameKind:
        """Queries the rule name kind for the cell's control"""
        key = "qry_ctl_rule_name_kind_result"
        if key in self._cache:
            result = self._cache[key]
        else:
            qry = QryPycRule(self._cell)
            result = self.qry_handler.handle(qry)
            self._cache[key] = result
        if Result.is_success(result):
            self.log.debug("qry_ctl_rule_name_kind_result: %s for cell: %s", result.data, self._cell.cell_obj)
            return result.data
        raise result.error

    def _qry_value(self) -> Iterable[Iterable[object]]:
        """Queries the value of the cell"""
        rule_kind = self._qry_ctl_rule_name_kind()
        state = self._qry_module_state()
        qry = QryValue(cell=self._cell, rule_kind=rule_kind, data=state.dd_data)
        result = self.qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def get_control_kind(self) -> CtlKind:
        """Gets the kind of control attached to the cell"""
        qry = QryCtlKind(self._cell)
        result = self.qry_handler.handle(qry)
        if Result.is_success(result):
            self.log.debug("get_control_kind() Control Kind: %s for cell: %s", result.data, self._cell.cell_obj)
            return result.data
        return CtlKind.UNKNOWN

    def add_default_control(self) -> Iterable[Iterable[object]]:
        """Adds a default string control to the cell and initializes empty code"""
        _ = ctl_director.create_control(self._cell, CtlKind.STRING)
        self._append_code("")
        try:
            self._cache.clear()
            # return self.get_value()
            return (("",),)
        except Exception:
            self.log.exception("add_default_control() Failed to get module state.")
            return ((None,),)
        # return state.dd_data.get("data")

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
            self.log.error("update_code() No control found for cell: %s", self._cell.cell_obj)
            return
        self.log.debug("update_code() Control  %s found for cell: %s", current_control, self._cell.cell_obj)
        cmd = CmdUpdateCode(cell=self._cell, mod=self._py_mod, code=code)
        self.cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to update code for cell: %s", self._cell.cell_obj)
            return
        self._cache.clear()
        rule = self.get_matched_rule()
        if rule is None:
            self.log.error("Failed to get matched rule for cell: %s", self._cell.cell_obj)
            return
        ctl_kind_qry = QryCtlKindFromRuleNameKind(rule.rule_kind)
        ctl_kind = self.qry_handler.handle(ctl_kind_qry)
        if ctl_kind != CtlKind.MAT_PLT_FIGURE and ctl_kind == current_control.control_kind:
            return
        if self.remove_control():
            self.log.debug("Control removed for cell: %s", self._cell.cell_obj)
        else:
            self.log.error("Failed to remove control for cell: %s", self._cell.cell_obj)
            return

        ctl = ctl_director.create_control(self._cell, ctl_kind)
        if ctl is not None:
            self.log.debug("Control created for cell: %s", self._cell.cell_obj)
        else:
            self.log.error("Failed to create control for cell: %s", self._cell.cell_obj)

    def auto_update(self) -> None:
        self.log.debug("auto_update() - Auto Updating Code")
        try:
            if self.init_calculate:
                self.log.debug("auto_update() - Document init CalculateAll has been called. Continuing.")
            else:
                self.log.debug("auto_update() - Document init CalculateAll not yet called. Skipping auto-update.")
                return
            code = self._qry_src_code()
            self.update_code(code)
            self.log.debug("auto_update() - Code Auto Updated")
        except Exception as e:
            self.log.debug("auto_update() -Failed to auto-update %s", e)

    def get_matched_rule(self) -> StateRuleT | None:
        """Gets the matching state rule for the cell's current state"""
        # do not cache this value. It may change when a cell get updated.
        try:
            state_rules = self._qry_state_rules()
            state = self._qry_module_state()
        except Exception:
            self.log.exception("Failed to get module state.")
            return None

        return state_rules.get_matched_rule(self._cell, state.dd_data)

    def is_control(self) -> bool:
        """Checks if the cell has a control attached"""
        ctl_kind = self.get_control_kind()
        return ctl_kind != CtlKind.UNKNOWN

    def is_source_cell(self) -> bool:
        """Checks if the cell is a source cell"""
        return self.cell.cell_obj in self._py_src_mgr

    def get_value(self) -> Iterable[Iterable[object]]:
        """
        Gets the value of the cell.
        """
        try:
            result = self._qry_value()
            # self.log.debug("get_value() result: %s", result)
            return result
        except Exception:
            self.log.exception("get_value() Failed to get module state.")
            return ((None,),)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._cell.cell_obj})>"

    @property
    def uri(self) -> str:
        """Gets the cell's URI"""
        if self._uri is None:
            self._uri = self._qry_uri()
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

    @property
    def init_calculate(self) -> bool:
        """Gets the initialization calculate status"""
        if self._init_calculate is None:
            self._init_calculate = self._qry_init_calculate()
        return self._init_calculate
