from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from libre_pythonista_lib.utils.result import Result


class CmdAddr(CmdBase, LogMixin, CmdCellT):
    """Sets the address of the cell such as ``sheet_index=0&cell_addr=A1``"""

    def __init__(self, cell: CalcCell, addr: str | Addr | None = None) -> None:
        """
        Initialize the command to set a cell's address.

        Args:
            cell (CalcCell): The cell to set the address for
            addr (str | Addr | None, optional): The address to set. If None, gets current address. Defaults to None.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = cast(str, NULL_OBJ)
        self._errors = True
        if addr is None:
            self._state = self._get_addr()
        else:
            try:
                self._state = Addr(str(addr))
            except Exception as err:
                self.log.error("Error setting cell address: %s", err)
                return
        self._errors = False
        self._state_changed = False
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_addr(self) -> Addr:
        """Gets the current cell address"""
        addr = f"sheet_index={self.cell.calc_sheet.sheet_index}&cell_addr={self.cell.cell_obj}"
        return Addr(addr)

    def _get_state(self) -> Addr:
        """Gets the target address state"""
        return self._state

    def _get_keys(self) -> KeyMaker:
        """Gets the KeyMaker instance for property keys"""
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _get_current_state(self) -> str:
        """Gets the current address state of the cell"""
        qry = QryAddr(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return ""

    @override
    def execute(self) -> None:
        """
        Executes the command to set the cell address.
        Sets success to True if address is set successfully.
        """
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
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_addr_key, value=self._state.value)
            self._execute_cmd(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell address")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """Internal method to undo the address change"""
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return
            if not self._current_state:
                self.log.debug("No Current State. Unable to undo.")
                return
            if self._current_state:
                cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_addr_key, value=self._current_state)
            else:
                # avoid circular import
                if TYPE_CHECKING:
                    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import (
                        CmdCellPropDel,
                    )
                else:
                    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
                cmd = CmdCellPropDel(cell=self.cell, name=self._keys.cell_addr_key)
            self._execute_cmd(cmd)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell address")

    @override
    def undo(self) -> None:
        """
        Public method to undo the address change.
        Only undoes if the command was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """Gets the cell being modified"""
        return self._cell
