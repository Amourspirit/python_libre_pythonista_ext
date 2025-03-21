from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind import (
        QryCtlKindFromRuleNameKind,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.map.qry_rule_name_kind_from_ctl_kind import (
        QryRuleNameKindFromCtlKind,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import SfaProvider
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.code.py_module import PyModule
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_code import CmdUpdateCode
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.common.map.qry_ctl_kind_from_rule_name_kind import QryCtlKindFromRuleNameKind
    from libre_pythonista_lib.cq.qry.calc.common.map.qry_rule_name_kind_from_ctl_kind import QryRuleNameKindFromCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import SfaProvider
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl import ctl_director
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rules import StateRules
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.log.log_mixin import LogMixin

    StateRuleT = Any

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_cell_item_facade.py


class CellItemFacade(LogMixin):
    def __init__(self, cell: CalcCell) -> None:
        LogMixin.__init__(self)
        self._cell = cell
        self._state_rules = StateRules()
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._py_mod = self._get_py_mod()
        self._uri = self._get_uri()
        self._src_provider = self._get_src_provider()
        self._py_src_mgr = PySourceManager(doc=self._cell.calc_doc, mod=self._py_mod, src_provider=self._src_provider)

    def _get_py_mod(self) -> PyModule:
        doc_globals = DocGlobals.get_current(self._cell.calc_doc.runtime_uid)
        key = "libre_pythonista_lib.code.py_module.PyModule"
        if key in doc_globals.mem_cache:
            return doc_globals.mem_cache[key]
        mod = PyModule()
        doc_globals.mem_cache[key] = mod
        return mod

    def _ensure_code_name(self) -> None:
        cmd = CmdCodeName(cell=self._cell, overwrite_existing=False)
        self._cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to set code name.")

    def _qry_module_state(self) -> ModuleStateItem | None:
        qry = QryModuleState(cell=self._cell, mod=self._py_mod)
        return self._qry_handler.handle(qry)

    def _get_uri(self) -> str:
        self._ensure_code_name()
        qry = QryCellUri(self._cell)
        return self._qry_handler.handle(qry)

    def _get_src_provider(self) -> PySrcProvider:
        return SfaProvider(self._uri)

    def has_control(self) -> bool:
        ctl_kind = self.get_control_kind()
        return ctl_kind != CtlKind.UNKNOWN

    def get_control_kind(self) -> CtlKind:
        qry = QryCtlKind(self._cell)
        return self._qry_handler.handle(qry)

    def add_default_control(self) -> Any:  # noqa: ANN401
        _ = ctl_director.create_control(self._cell, CtlKind.STRING)
        self._append_code("")
        state = self._qry_module_state()
        if state is None:
            return None
        return state.dd_data.get("data")

    def _append_code(self, code: str) -> None:
        cmd = CmdAppendCode(cell=self._cell, mod=self._py_mod, code=code, src_provider=self._src_provider)
        self._cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to append code.")

    def get_control(self) -> CtlBase | None:
        return ctl_director.get_control(self._cell)

    def remove_control(self) -> bool:
        return ctl_director.remove_control(self._cell)

    def update_code(self, code: str) -> None:
        current_control = self.get_control()
        if current_control is None:
            self.log.error("update_code() No control found.")
            return
        cmd = CmdUpdateCode(cell=self._cell, mod=self._py_mod, code=code, src_provider=self._src_provider)
        self._cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to update code.")
            return
        rule = self.get_matched_rule()
        if rule is None:
            self.log.error("Failed to get matched rule.")
            return
        rule.rule_kind
        ctl_kind_qry = QryCtlKindFromRuleNameKind(rule.rule_kind)
        ctl_kind = self._qry_handler.handle(ctl_kind_qry)
        if ctl_kind == current_control.control_kind:
            return
        if not self.remove_control():
            self.log.error("Failed to remove control.")
            return
        _ = ctl_director.create_control(self._cell, ctl_kind)

    def get_matched_rule(self) -> StateRuleT | None:
        # do not cache this value. It may change when a cell get updated.
        state = self._qry_module_state()
        if state is None:
            return None
        return self._state_rules.get_matched_rule(self._cell, state.dd_data)
