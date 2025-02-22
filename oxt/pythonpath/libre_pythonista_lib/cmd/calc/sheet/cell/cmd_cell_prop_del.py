from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.loader import Lo
from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcCell
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

# this class should be call in:
# libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache.CmdHandlerSheetCache

# this class should be called with:
# pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_handler_cell_cache.CmdHandlerCellCache


class CmdCellPropDel(LogMixin, CmdCellT):
    """Deletes a custom property of a cell"""

    def __init__(self, cell: CalcCell, name: str) -> None:  # noqa: ANN401
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._cell = cell
        self._name = name
        self._kind = CalcCmdKind.CELL
        self._current_value = self._get_current_value()

    def _get_current_value(self) -> Any:  # noqa: ANN401
        qry = QryCellPropValue(cell=self._cell, name=self._name)
        handler = QryHandler()

        return handler.handle(qry)  # returns NULL_OBJ if not found

    def execute(self) -> None:
        self._success = False
        try:
            self._cell.remove_custom_property(self._name)
        except Exception:
            self.log.exception("Error setting cell Code")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        if self._current_value is NULL_OBJ:
            try:
                if self._cell.has_custom_property(self._name):
                    self._cell.remove_custom_property(self._name)
            except Exception:
                self.log.exception("Error undoing cell Code")
        else:
            try:
                self._cell.set_custom_property(self._name, self._current_value)
                self.log.debug("Successfully executed undo command.")
                return
            except Exception:
                self.log.exception("Error undoing cell Code")

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.CELL``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
