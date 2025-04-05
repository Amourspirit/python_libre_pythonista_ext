from __future__ import annotations

from typing import TYPE_CHECKING, Any
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.feature_kind import FeatureKind
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.feature_kind import FeatureKind
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QryMatPlotFigure(QryBase, LogMixin, QryCellT[Any]):
    """Sets Control MatPlotFigure properties"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
            ctl (Ctl): Control to populate.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _set_control_props(self) -> None:
        """Sets the control properties"""
        if self._ctl is None:
            self.log.debug("_set_control_props() No control found. Returning.")
            return
        self._ctl.ctl_props = (
            CtlPropKind.CTL_ORIG,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )

    def _set_control_kind(self) -> None:
        if self._ctl is None:
            self.log.debug("_set_control_kind() No control found. Returning.")
            return
        self._ctl.control_kind = CtlKind.MAT_PLT_FIGURE

    def _set_control_features(self) -> None:
        """Sets the control features"""
        if self._ctl is None:
            self.log.debug("_set_control_features() No control found. Returning.")
            return
        self._ctl.supported_features = set()
        self._ctl.supported_features.add(FeatureKind.ADD_CTL)
        self._ctl.supported_features.add(FeatureKind.REMOVE_CTL)
        self._ctl.supported_features.add(FeatureKind.GET_RULE_NAME)
        self._ctl.supported_features.add(FeatureKind.GET_CELL_POS_SIZE)

    def execute(self) -> Any:  # noqa: ANN401
        """
        Executes the query to get control

        Returns:
            Any: The control or None if it does not exist.
        """

        try:
            self._set_control_kind()
            self._set_control_props()
            self._set_control_features()
            self.log.debug("Set Properties done for cell %s", self.cell.cell_obj)
            return self._ctl
        except Exception as e:
            self.log.error("Error executing command: %s", e)
        return None

    @property
    def cell(self) -> CalcCell:
        return self._cell
