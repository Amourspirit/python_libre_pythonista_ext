from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.const import (
        DISPATCH_CODE_EDIT_MB,
        DISPATCH_DF_STATE,
        DISPATCH_DS_STATE,
        DISPATCH_DATA_TBL_STATE,
        DISPATCH_CODE_DEL,
    )
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.const import (
        DISPATCH_CODE_EDIT_MB,
        DISPATCH_DF_STATE,
        DISPATCH_DS_STATE,
        DISPATCH_DATA_TBL_STATE,
        DISPATCH_CODE_DEL,
    )


class CellDispatchState2:
    """Class to get the dispatch state of a cell."""

    def __init__(self, cell: CalcCell) -> None:
        self._cell = cell
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._cmd_handler = CmdHandlerFactory.get_cmd_handler()
        self._dispatch_allowed = {
            DISPATCH_CODE_EDIT_MB,
            DISPATCH_DF_STATE,
            DISPATCH_DS_STATE,
            DISPATCH_DATA_TBL_STATE,
            DISPATCH_CODE_DEL,
        }

    def is_dispatch_enabled(self, cmd: str) -> bool:
        if cmd in self._dispatch_allowed:
            if not self.sheet_locked:
                return True
            return not self.cell_locked
        return True

    def is_protected(self) -> bool:
        """
        Gets if the cell is protected.
        If the sheet not protected then the cell is not considered to be protected.


        Returns:
            bool: True if the sheet is protected and the cell is protected.
        """
        if not self.sheet_locked:  # unlocked
            return False
        return self.cell_locked

    def _qry_ctl_kind(self) -> CtlKind:
        qry = QryCtlKind(self._cell)
        result = self._qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        return CtlKind.UNKNOWN

    def get_rule_dispatch_cmd(self) -> str:
        """
        Gets the dispatch command that matches the current pyc rule.

        Returns:
            str: The dispatch command.
        """
        ctl_kind = self._qry_ctl_kind()
        if ctl_kind == CtlKind.DATA_FRAME:
            return DISPATCH_DF_STATE
        if ctl_kind == CtlKind.SERIES:
            return DISPATCH_DS_STATE
        if ctl_kind == CtlKind.DATA_TABLE:
            return DISPATCH_DATA_TBL_STATE
        return ""

    def get_state(self) -> StateKind:
        """
        Gets the state

        Returns:
            StateKind: The state.
        """
        qry = QryState(self._cell)
        result = self._qry_handler.handle(qry)
        if Result.is_success(result):
            return result.data
        return StateKind.UNKNOWN

    def set_state(self, value: StateKind) -> None:
        """
        Sets the state

        Args:
            value (StateKind): The state.
        """
        cmd = CmdState(self._cell, value)
        self._cmd_handler.handle(cmd)
        if not cmd.success:
            raise Exception("Failed to set state.")

    # region Properties
    @property
    def sheet_locked(self) -> bool:
        return self._cell.calc_sheet.is_sheet_protected()

    @property
    def cell_locked(self) -> bool:
        return self._cell.cell_protection.is_locked

    # endregion Properties
