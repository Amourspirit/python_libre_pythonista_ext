from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_shape import QryShape
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_shape import QryShape
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker


class CmdShape(CmdBase, LogMixin, CmdCellT):
    """Sets the shape of the cell such as ``SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf``"""

    def __init__(self, cell: CalcCell, name: str) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the shape for.
            name (str): Shape name to set such as ``SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf``. Cannot be empty.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.kind = CalcCmdKind.CELL
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._current_state = cast(str, NULL_OBJ)
        self._state_changed = False
        self._errors = True
        if not name:
            self.log.error("Error setting shape: name is empty")
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
        qry = QryShape(cell=self.cell)
        return self._execute_qry(qry)

    @override
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
            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.ctl_shape_key, value=self._state)
            self._execute_cmd(cmd)
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell shape")
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
                cmd = CmdCellPropSet(cell=self.cell, name=self._keys.ctl_shape_key, value=self._current_state)
            else:
                if TYPE_CHECKING:
                    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape_del import (
                        CmdShapeDel,
                    )
                else:
                    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape_del import CmdShapeDel

                cmd = CmdShapeDel(cell=self.cell)
            self._execute_cmd(cmd)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell shape")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
