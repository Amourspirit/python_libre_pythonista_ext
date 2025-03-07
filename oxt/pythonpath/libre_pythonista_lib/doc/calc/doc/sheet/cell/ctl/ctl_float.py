from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase


class CtlFloat(CtlBase):
    # region Properties

    @property
    def shape_name(self) -> str:
        return self.ctl.ctl_shape_name

    @property
    def label(self) -> str:
        return self.ctl.label

    # endregion Properties
