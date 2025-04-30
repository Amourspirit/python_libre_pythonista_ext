from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_shape_base import CtlShapeBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_shape_base import CtlShapeBase


class CtlPdSeries(CtlShapeBase):
    @property
    def state_kind(self) -> StateKind:
        """Gets the state for the cell. Maybe StateKind.UNKNOWN."""
        return self.ctl.ctl_state
