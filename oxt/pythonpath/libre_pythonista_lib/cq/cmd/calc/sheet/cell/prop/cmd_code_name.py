from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker


class CmdCodeName(CmdBase, LogMixin, CmdCellT):
    """Sets the code name of the cell such as ``id_l6fiSBIiNVcncf``"""

    def __init__(self, cell: CalcCell, name: str) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the code name for.
            name (str): Code name to set. Cannot be empty.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._state_changed = False
        self.kind = CalcCmdKind.CELL
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = cast(str, NULL_OBJ)
        self._errors = True
        if not name:
            self.log.error("Error setting Code Name: name is empty")
            return
        self._state = name
        self._errors = False

    def _get_state(self) -> str:
        # use method to make possible to mock for testing
        return self._state

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _get_current_state(self) -> str:
        qry = QryCodeName(cell=self.cell)
        return self._execute_qry(qry)

    def execute(self) -> None:
        self.success = False
        if self._errors:
            self.log.error("Errors occurred during initialization. Unable to execute command.")
            return

        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()
        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()

        self._state_changed = False
        try:
            if self._current_state and self._get_state() == self._current_state:
                self.log.debug("State is already set.")
                self.success = True
                return
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_code_name, value=self._state)
            self._execute_cmd(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell Code Name")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return

            if self._current_state:
                cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_code_name, value=self._current_state)
            else:
                if TYPE_CHECKING:
                    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import (
                        CmdCodeNameDel,
                    )
                else:
                    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name_del import CmdCodeNameDel
                cmd = CmdCodeNameDel(cell=self.cell)

            self._execute_cmd(cmd)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code Name")

    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
