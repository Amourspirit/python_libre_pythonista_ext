from __future__ import annotations

from typing import TYPE_CHECKING, Any
from com.sun.star.container import NoSuchElementException
from ooodev.calc import CalcCell
from ooodev.calc import CalcSheet, SpreadsheetDrawPage
from ooodev.draw.shapes import DrawShape

if TYPE_CHECKING:
    from ooodev.form.controls.form_ctl_base import FormCtlBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result

    FormCtlBase = Any


class QryCtlCurrent(QryBase, LogMixin, QryCellT[Result[FormCtlBase, None] | Result[None, Exception]]):
    """Gets the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_shape(self) -> Result[DrawShape[SpreadsheetDrawPage[CalcSheet]], None] | Result[None, Exception]:
        """Gets the control shape or None."""
        qry_shape = QryLpShape(cell=self.cell)
        return self._execute_qry(qry_shape)

    def execute(self) -> Result[FormCtlBase, None] | Result[None, Exception]:
        """ "
        Executes the query and get the control if it exists.

        Assigns ``control`` to ``ctl`` if it exist.

        Returns:
            Any: The control or None if it does not exist.
        """
        shape_result = self._get_shape()
        if Result.is_failure(shape_result):
            self.log.debug("No shape found. Returning None.")
            return shape_result
        shape = shape_result.data

        ctl = shape.component.getControl()  # type: ignore
        if ctl is None:
            self.log.debug("No control found for shape. Returning None.")
            return Result.failure(Exception("No control found for shape."))

        try:
            from ooodev.form.controls.from_control_factory import FormControlFactory

            factory = FormControlFactory(draw_page=self.cell.calc_sheet.draw_page.component, lo_inst=self.cell.lo_inst)
            factory_ctl = factory.get_control_from_model(ctl)
            self.log.debug("Found Control from factory")
            if self._ctl is not None:
                self._ctl.control = factory_ctl
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            if factory_ctl is None:
                return Result.failure(Exception("No control found for shape."))
            return Result.success(factory_ctl)
        except NoSuchElementException:
            self.log.warning("NoSuchElementException error from FormControlFactory Control not found.")
        return Result.failure(Exception("NoSuchElementException error from FormControlFactory Control not found."))

    @property
    def cell(self) -> CalcCell:
        return self._cell
