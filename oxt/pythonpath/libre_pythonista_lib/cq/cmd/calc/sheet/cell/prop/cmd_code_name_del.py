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
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_set import CmdCellExtraSet
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_del import CmdCellExtraDel
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_set import CmdCellExtraSet
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_del import CmdCellExtraDel
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.utils.result import Result


class CmdCodeNameDel(CmdBase, LogMixin, CmdCellT):
    """
    Deletes the code name from custom properties of the cell if it exists.
    Removes the code name from extra data if it exists.
    """

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
        self._code_name_removed = False
        self._current_code_name = cast(str, NULL_OBJ)
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_keys(self) -> KeyMaker:
        """Gets KeyMaker instance through query execution"""
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _qry_code_name(self) -> str:
        """Queries the code name for the cell"""
        qry = QryCodeName(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _cmd_cell_extra_set_code_name_del(self) -> None:
        """
        Creates a CmdCellExtraDel command to delete the code name in extra data.

        Returns:
            CmdCellExtraDel instance
        """
        cmd = CmdCellExtraDel(cell=self.cell, name="code_name")
        self._execute_cmd(cmd)
        if cmd.success:
            self._code_name_removed = True
        else:
            self.log.error("Failed to execute command: CmdCellExtraDel for cell %s", self._cell.cell_obj)

    def _cmd_cell_extra_set_code_name(self) -> None:
        """
        Create a CmdCellExtraSet command to set the code name in extra data.

        Returns:
            CmdCellExtraSet instance
        """
        if not self._current_code_name:
            return
        cmd = CmdCellExtraSet(cell=self.cell, name="code_name", value=self._current_code_name)
        self._execute_cmd(cmd)
        if cmd.success:
            self._code_name_removed = False
        else:
            self.log.error("Failed to execute command: CmdCellExtraSet for cell %s", self._cell.cell_obj)

    @override
    def execute(self) -> None:
        """
        Executes the command to delete the code name.
        Sets success to True if operation succeeds, False otherwise.
        """
        self.success = False

        try:
            if self._current_code_name is NULL_OBJ:
                self._current_code_name = self._qry_code_name()
            if not isinstance(self._keys, KeyMaker):
                self._keys = self._get_keys()
            if not self._current_code_name:
                self.log.debug("Property does not exist on cell. Nothing to delete.")
                self.success = True
                return
            cmd = CmdCellPropDel(cell=self.cell, name=self._keys.cell_code_name)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute command: CmdCellPropDel for cell %s", self._cell.cell_obj)
                return
            self._cmd_cell_extra_set_code_name_del()

        except Exception:
            self.log.exception("Error deleting cell Code Name")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to restore the previous state if needed.
        Attempts to restore both the property and extra data.
        """
        try:
            if not self._current_code_name:
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

            cmd = CmdCellPropSet(cell=self.cell, name=self._keys.cell_code_name, value=self._current_code_name)
            self._execute_cmd(cmd)
            if cmd.success:
                if self._code_name_removed:
                    self._cmd_cell_extra_set_code_name()
                self.log.debug("Successfully executed undo command.")
            else:
                self.log.error("Failed to execute undo command: CmdCellPropSet for cell %s", self._cell.cell_obj)
        except Exception:
            self.log.exception("Error undoing cell Code Name")

    @override
    def undo(self) -> None:
        """
        Public undo method. Only performs undo if the original command was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """Returns the cell instance"""
        return self._cell
