from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.feature_kind import FeatureKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_simple import QrySimple
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_simple import QrySimple
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.feature_kind import FeatureKind
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override


class QryPdDf(QrySimple):
    """Sets Control Pandas DataFrame properties"""

    @override
    def _set_control_kind(self) -> None:
        if self._ctl is None:
            self.log.debug("_set_control_kind() No control found. Returning.")
            return
        self._ctl.control_kind = CtlKind.DATA_FRAME

    @override
    def _set_control_features(self) -> None:
        """Sets the control features"""
        super()._set_control_features()
        if self._ctl is None:
            self.log.debug("_set_control_features() No control found. Returning.")
            return
        self._ctl.supported_features.add(FeatureKind.ADD_CTL)
        self._ctl.supported_features.add(FeatureKind.REMOVE_CTL)
        self._ctl.supported_features.add(FeatureKind.UPDATE_CTL)
        self._ctl.supported_features.add(FeatureKind.UPDATE_CTL_ACTION)
        self._ctl.supported_features.add(FeatureKind.GET_RULE_NAME)
        self._ctl.supported_features.add(FeatureKind.GET_CELL_POS_SIZE)
