from __future__ import annotations
from typing import TYPE_CHECKING

from com.sun.star.awt import XActionListener
from ooodev.utils.kind.language_kind import LanguageKind


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from ooodev.form.controls.form_ctl_base import FormCtlBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_script_loc import QryCtlScriptLoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_location import QryLocation
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_script_loc import QryCtlScriptLoc
    from libre_pythonista_lib.cq.qry.general.qry_location import QryLocation
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class CmdSetLocation(CmdBase, LogMixin, CmdCellCtlT):
    """Creates a simple control"""

    def __init__(self, cell: CalcCell, ctl: FormCtlBase) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_script_loc(self) -> str:
        qry = QryCtlScriptLoc(cell=self.cell)
        return self._execute_qry(qry)

    def _get_location(self) -> str:
        qry = QryLocation()
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        self.success = False

        self._state_changed = False
        try:
            script_loc = self._get_script_loc()
            location = self._get_location()
            self._ctl.assign_script(
                interface_name=XActionListener,  # type: ignore
                method_name="actionPerformed",
                script_name=script_loc,
                loc=location,
                language=LanguageKind.PYTHON,
                auto_remove_existing=True,
            )
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting code name")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        try:
            self._ctl.remove_script(
                interface_name=XActionListener,  # type: ignore
                method_name="actionPerformed",
            )
        except Exception:
            self.log.exception("Error undoing script")
            return
        self.log.debug("Successfully executed undo command.")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
