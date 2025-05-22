from __future__ import annotations
from typing import TYPE_CHECKING

from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point

if TYPE_CHECKING:
    from com.sun.star.drawing import ControlShape  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_pd_df import QryPdDf
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_pd_df import QryPdDf

    ControlShape = object


class CmdPdDf(CmdSimple):
    @override
    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.DATA_FRAME

    @override
    def _on_executing(self, ctl: Ctl) -> None:
        qry = QryPdDf(self.cell, ctl)
        self._execute_qry(qry)

    @override
    def _set_shape_size(self, shape: ControlShape) -> None:
        """Sets the shape size"""
        qry = QryCtlCellSizePos(cell=self.cell)
        size_pos = self._execute_qry(qry)

        width = int(size_pos.width)
        height = int(size_pos.height)
        x = int(size_pos.x)
        y = int(size_pos.y)
        new_sz = Size(width, height)
        shape.setSize(new_sz)
        shape.setPosition(Point(x, y))
