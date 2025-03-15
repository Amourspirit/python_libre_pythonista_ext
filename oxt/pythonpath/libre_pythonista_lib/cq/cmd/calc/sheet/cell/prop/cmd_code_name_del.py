from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker


class CmdCodeNameDel(CmdBase, LogMixin, CmdCellT):
    """Deletes the code name of the cell if it exists"""

    def __init__(self, cell: CalcCell) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to delete the code name for.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._keys = cast(KeyMaker, None)
        self._current_state = cast(str, NULL_OBJ)

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _get_current_state(self) -> str:
        qry = QryCodeName(cell=self.cell)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()
        if not isinstance(self._keys, KeyMaker):
            self._keys = self._get_keys()

        self.success = False
        try:
            if not self._current_state:
                self.log.debug("Property does not exist on cell. Nothing to delete.")
                self.success = True
                return
            cmd = CmdCellPropDel(cell=self.cell, name=self._keys.cell_code_name)
            self._execute_cmd(cmd)
        except Exception:
            self.log.exception("Error deleting cell Code Name")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if not self._current_state:
                self.log.debug("No Current State. Unable to undo.")
                return

            if not isinstance(self._keys, KeyMaker):
                self._keys = self._get_keys()

            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import (
                    CmdCellPropSet,
                )
            else:
                from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet

            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_code_name, value=self._current_state)
            self._execute_cmd(cmd)
            if cmd.success:
                self.log.debug("Successfully executed undo command.")
            else:
                self.log.error("Failed to execute undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code Name")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
