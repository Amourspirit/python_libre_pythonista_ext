# region Imports
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod

from ooodev.calc import CalcCell
from ooodev.events.args.cancel_event_args import CancelEventArgs


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import CONTROL_ADDING
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_is_cell_in_src import QryIsCellInSrc
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_pyc_array_formula import (
        QryCellIsPycArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import (
        CmdSetArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
    from libre_pythonista_lib.const.event_const import CONTROL_ADDING
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_is_cell_in_src import QryIsCellInSrc
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_pyc_array_formula import (
        QryCellIsPycArrayFormula,
    )
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import CmdSetArrayFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula

# endregion Imports


class CellCodeEdit(LogMixin, ABC):
    """Cell code edit class."""

    def __init__(self, inst_id: str, cell: CalcCell, url_str: str = "", src_code: str = "") -> None:
        """
        Initialize the CellCodeEdit class.

        Args:
            inst_id (str): instance id that represents this instance in a cache or dictionary.
            cell (CalcCell): The cell to edit.
            url_str (str, optional): The url string. Defaults to "".
            src_code (str, optional): Source Code. Usually when provided it will take precedent or showing a dialog to get code. Defaults to "".
        """
        super().__init__()
        self.log.debug("init: inst_id=%s, cell=%s, url=%s", inst_id, cell, url_str)
        self.cell = cell
        self._facade = CellItemFacade(cell=self.cell)
        self.url = url_str
        self.inst_id = inst_id
        self.src_code = src_code
        self._listeners = CodeCellListeners(self.cell.calc_doc)
        self._is_formula_array = False
        self._shared_event = SharedEvent()
        self._fn_on_adding_control = self._on_adding_control
        self._shared_event.subscribe_event(CONTROL_ADDING, self._fn_on_adding_control)

    def _qry_is_cell_in_src(self) -> bool:
        """Check if the cell is in the source code manager."""
        qry = QryIsCellInSrc(cell=self.cell, mod=self._facade.py_mod)
        return self._facade.qry_handler.handle(qry)

    def _qry_is_pyc_array_formula(self) -> bool:
        """Check if the cell formula is a pyc array formula."""
        qry = QryCellIsPycArrayFormula(cell=self.cell)
        return self._facade.qry_handler.handle(qry)

    def update_cell(self) -> None:
        """
        Do the work and update the cell.

        If the code for the cell is to be update then this method ensures the cell formula is updates and triggers the necessary events.
        """
        with self.log.indent(True):
            try:
                self.log.debug("dispatch: cell=%s", self.cell.cell_obj)
                self._is_formula_array = False

                if not self._qry_is_cell_in_src():
                    self.log.error("Cell %s is not in the cache.", self.cell.cell_obj)
                    return

                result = self.edit_code()
                if result and self.cell.calc_doc.component.isAutomaticCalculationEnabled():
                    # the purpose of writing the formulas back to the cell(s) is to trigger the recalculation
                    # cm = CellMgr(self.cell.calc_doc)
                    # https://ask.libreoffice.org/t/mark-a-calc-sheet-cell-as-dirty/106659
                    # suspend the listeners for this cell
                    with self._listeners.suspend_listener_ctx(self.cell):
                        # suspend the listeners for this cell
                        formula = self.cell.component.getFormula()
                        if not formula:
                            self.log.error("Cell %s has no formula.", self.cell.cell_obj)
                            return

                        self._is_formula_array = self._qry_is_pyc_array_formula()
                        if self._is_formula_array:
                            formula = formula.lstrip("{").rstrip("}")

                        if self._is_formula_array:
                            cmd = CmdSetArrayFormula(cell=self.cell, formula=formula)
                            self._facade.cmd_handler.handle(cmd)
                            if not cmd.success:
                                self.log.error("Failed to execute command for cell %s.", self.cell.cell_obj)
                                return
                        else:
                            self.log.debug("Resetting formula")
                            cmd = CmdSetFormula(cell=self.cell, formula=formula)
                            self._facade.cmd_handler.handle(cmd)
                            if not cmd.success:
                                self.log.error("Failed to execute command for cell %s.", self.cell.cell_obj)
                                return
                        self.cell.calc_doc.component.calculate()
            except Exception:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self.log.exception("Error:")
                return

    def _on_adding_control(self, src: Any, event: CancelEventArgs) -> None:  # noqa: ANN401
        # When cursor.setArrayFormula(formula) is called in dispatch
        # it cause a bunch of events to be fired.
        # When a cell is displayed as an array this cause a control to be added in the cell.
        # The fix is to cancel the adding of controls here.
        # The event is fired in pythonpath.libre_pythonista_lib.cell.ctl.simple_ctl.SimpleCtl.add_ctl
        if self._is_formula_array:
            event.cancel = True

    @abstractmethod
    def edit_code(self) -> bool: ...
