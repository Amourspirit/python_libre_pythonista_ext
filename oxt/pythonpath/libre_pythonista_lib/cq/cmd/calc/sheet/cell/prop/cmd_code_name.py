from __future__ import annotations
from typing import cast, List, TYPE_CHECKING

from ooodev.utils import gen_util

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_set import CmdCellExtraSet
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_set import CmdCellExtraSet
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class CmdCodeName(CmdBase, LogMixin, CmdCellT):
    """Sets the code name of the cell such as ``id_l6fiSBIiNVcncf``"""

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the command with a cell.

        Args:
            cell: The CalcCell instance to set the code name for
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._success_commands: List[CmdT] = []
        self._current_code_name = None
        self._code_name = None
        self._keys = cast(KeyMaker, None)
        self._current_dict_code_name = self.cell.extra_data.get("code_name", "")

    def get_gen_code_name(self) -> str:
        """
        Generate a random code name if one hasn't been generated yet.

        Returns:
            A string in format "id_" followed by 14 random alphanumeric characters
        """
        if self._code_name is None:
            self._code_name = "id_" + gen_util.Util.generate_random_alpha_numeric(14)
        return self._code_name

    def _get_code_name(self) -> str:
        """
        Get the current code name using QryCodeName query.

        Returns:
            The current code name of the cell
        """
        qry = QryCodeName(cell=self.cell)
        return self._execute_qry(qry)

    def _get_keys(self) -> KeyMaker:
        """
        Get KeyMaker instance using QryKeyMaker query.

        Returns:
            KeyMaker instance containing key definitions
        """
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Execute the command to set a new code name for the cell.
        Updates both cell properties and extra data.
        """
        self.success = False
        self._state_changed = False
        self._success_commands.clear()
        try:
            if self._current_code_name is None:
                self._current_code_name = self._get_code_name()

            if not isinstance(self._keys, KeyMaker):
                self._keys = self._get_keys()

            code_name = self.get_gen_code_name()
            cmd_prop_code_name = CmdCellPropSet(cell=self.cell, name=self._keys.cell_code_name, value=code_name)
            self._execute_cmd(cmd_prop_code_name)

            if cmd_prop_code_name.success:
                self._success_commands.append(cmd_prop_code_name)
            else:
                self.log.error("Error setting cell code name")
                return

            cmd_cell_extra_set = CmdCellExtraSet(cell=self.cell, name="code_name", value=code_name)
            self._execute_cmd(cmd_cell_extra_set)
            if cmd_cell_extra_set.success:
                self._success_commands.append(cmd_cell_extra_set)
            else:
                self.log.error("Error setting cell extra data")
                self._undo()
                return

            self._state_changed = True
        except Exception:
            self.log.exception("Error setting code name")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo changes made by execute().
        Restores previous code name state.
        """
        try:
            for cmd in self._success_commands:
                self._execute_cmd_undo(cmd)
            self._success_commands.clear()
            if not self._state_changed:
                return
            if self._current_dict_code_name:
                self.cell.extra_data.code_name = self._current_dict_code_name
            else:
                if self.cell.extra_data.has("code_name"):
                    del self.cell.extra_data["code_name"]
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code Name")

    @override
    def undo(self) -> None:
        """
        Public method to undo the command if it was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell associated with this command.

        Returns:
            The CalcCell instance
        """
        return self._cell
