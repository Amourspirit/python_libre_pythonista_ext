from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_is_update_required import (
        QryIsUpdateRequired,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import (
        CmdSetArrayFormula,
    )
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_is_update_required import QryIsUpdateRequired
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import CmdSetArrayFormula


class CmdUpdateArrayFormula(CmdBase, LogMixin, CmdCellT):
    def __init__(self, cell: CalcCell) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_is_update_required(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryIsUpdateRequired(cell=self.cell)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        self.success = False
        try:
            if not self._qry_is_update_required():
                self.log.debug("No update required.")
                self.success = True
                return
            cmd = CmdSetArrayFormula(cell=self.cell)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute command for cell %s.", self.cell.cell_obj)
                return
        except Exception:
            self.log.exception("Error updating array formula for cell %s.", self.cell.cell_obj)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
