from __future__ import annotations
from typing import cast, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_delete_formula import CmdDeleteFormula
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_delete_code import CmdDeleteCode
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_delete_control import CmdDeleteControl
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.general.cmd_batch import CmdBatch
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener_del import (
        CmdCodeListenerDel,
    )
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_delete_formula import CmdDeleteFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener_del import CmdCodeListenerDel
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_delete_code import CmdDeleteCode
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_delete_control import CmdDeleteControl
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.general.cmd_batch import CmdBatch
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.style.style_t import StyleT
    from libre_pythonista_lib.utils.custom_ext import override


class CmdDeleteLpCell(CmdBase, LogMixin, CmdCellT):
    def __init__(self, cell: CalcCell, mod: Union[PyModuleT, None] = None, style: Union[StyleT, None] = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._style = style
        self._batch = cast(CmdBatch, None)
        self.log.debug("init done for cell %s", self.cell.cell_obj)

    @override
    def execute(self) -> None:
        """
        Executes the control delete command.

        Removes the cell's control.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False

        try:
            if self._batch is None:
                # make sure the listener is removed first.
                cmd_del_listener = CmdCodeListenerDel(cell=self.cell)
                cmd_del_control = CmdDeleteControl(cell=self.cell, mod=self._mod)
                cmd_del_code = CmdDeleteCode(cell=self.cell, mod=self._mod)
                cmd_del_formula = CmdDeleteFormula(cell=self.cell, style=self._style)
                self._batch = CmdBatch(cmd_del_listener, cmd_del_formula, cmd_del_control, cmd_del_code)
                self._execute_cmd(self._batch)
                if not self._batch.success:
                    self.log.error("Failed to execute batch command.")
                    self._undo()
                    return
        except Exception:
            self.log.exception("Error setting cell address")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal undo implementation that restores the previous control state.
        """
        try:
            if self._batch is None:
                self.log.debug("Batch is None. Nothing to undo.")
                return
            self._batch.undo()
            self._batch = cast(CmdBatch, None)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell address")

    @override
    def undo(self) -> None:
        """
        Public undo method that only executes if the command was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """Gets the cell this command operates on"""
        return self._cell
