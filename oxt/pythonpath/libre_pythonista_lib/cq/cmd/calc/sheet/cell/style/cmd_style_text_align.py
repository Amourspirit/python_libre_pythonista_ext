from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast

from com.sun.star.awt import XActionListener
from ooodev.utils.gen_util import NULL_OBJ
from ooodev.utils.kind.language_kind import LanguageKind
from ooodev.format.inner.direct.calc.alignment.text_align import HoriAlignKind
from ooodev.units import UnitPT


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from ooodev.form.controls.form_ctl_base import FormCtlBase
    from ooodev.format.proto.calc.alignment.text_align_t import TextAlignT
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

    TextAlignT = Any


class CmdStyleTextAlign(CmdBase, LogMixin, CmdCellCtlT):
    """Applies text alignment style and indent to cell."""

    def __init__(self, cell: CalcCell, hori_align: HoriAlignKind = HoriAlignKind.LEFT, indent: int = 14) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the code name for.
            hori_align (HoriAlignKind, optional): Horizontal alignment. Defaults to ``HoriAlignKind.LEFT``.
            indent (int, optional): Indent in points. Defaults to ``14``.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._hori_align = hori_align
        self._indent = UnitPT(indent)
        self._current_state = cast(TextAlignT, NULL_OBJ)

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
        if self._current_state is NULL_OBJ:
            self._current_state = self.cell.style_align_text_get()
        try:
            self.cell.style_align_text(hori_align=self._hori_align, indent=self._indent)
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
            if self._current_state is not None and self._current_state is not NULL_OBJ:
                self.cell.style_align_text(self._current_state.prop_hori_align, self._current_state.prop_indent)
        except Exception:
            self.log.exception("Error undoing style")
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
