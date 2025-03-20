from __future__ import annotations

from typing import TYPE_CHECKING, Any
from com.sun.star.container import NoSuchElementException
from ooodev.calc import CalcCell
from ooodev.calc import CalcSheet, SpreadsheetDrawPage
from ooodev.draw.shapes import DrawShape

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape as QryShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape as QryShapeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QrySimple(QryBase, LogMixin, QryCellT[Any]):
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

    def _get_shape_name(self) -> str:
        qry_shape = QryShapeName(cell=self.cell)
        return self._execute_qry(qry_shape)

    def _get_shape(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]] | None:
        """Gets the control shape or None."""
        qry_shape = QryLpShape(cell=self.cell)
        return self._execute_qry(qry_shape)

    def _set_control_props(self) -> None:
        """Sets the control properties"""
        if self._ctl is None:
            self.log.debug("_set_control_props() No control found. Returning.")
            return
        self._ctl.ctl_props = (
            CtlPropKind.CTL_SHAPE,
            CtlPropKind.CTL_ORIG,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )

    def _set_control_kind(self) -> None:
        if self._ctl is None:
            self.log.debug("_set_control_kind() No control found. Returning.")
            return
        self._ctl.control_kind = CtlKind.SIMPLE_CTL

    def execute(self) -> Any:  # noqa: ANN401
        """ "
        Executes the query and get the control if it exists.

        Assigns ``control`` to ``ctl`` if it exist.

        Returns:
            Any: The control or None if it does not exist.
        """
        shape = self._get_shape()
        if shape is None:
            self.log.debug("No shape found. Returning None.")
            return None

        ctl = shape.component.getControl()  # type: ignore
        if ctl is None:
            self.log.debug("No control found for shape. Returning None.")
            return None

        try:
            from ooodev.form.controls.from_control_factory import FormControlFactory

            factory = FormControlFactory(draw_page=self.cell.calc_sheet.draw_page.component, lo_inst=self.cell.lo_inst)
            factory_ctl = factory.get_control_from_model(ctl)
            self.log.debug("Found Control from factory")
            if self._ctl is not None:
                self._ctl.control = factory_ctl
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            self._set_control_kind()
            self._set_control_props()
            return factory_ctl
        except NoSuchElementException:
            self.log.warning("NoSuchElementException error from FormControlFactory Control not found.")
        return None

    @property
    def cell(self) -> CalcCell:
        return self._cell
