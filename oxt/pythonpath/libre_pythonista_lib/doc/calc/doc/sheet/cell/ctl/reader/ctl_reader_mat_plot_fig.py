from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_control_img_name import QryControlImgName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_modify_trigger_event import (
        QryCtlModifyTriggerEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_rule_name_kind import (
        QryCtlRuleNameKind,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader import CtlReader
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_control_img_name import QryControlImgName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_modify_trigger_event import QryCtlModifyTriggerEvent
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_rule_name_kind import QryCtlRuleNameKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader import CtlReader
    from libre_pythonista_lib.utils.custom_ext import override


class CtlReaderMatPlotFig(CtlReader):
    @override
    def append_query(self) -> None:
        self.append(QryControlImgName(self.cell, self.ctl))
        self.append(QryCtlShapeName(self.cell, self.ctl))
        self.append(QryCtlRuleNameKind(self.cell, self.ctl))
        self.append(QryCtlModifyTriggerEvent(self.cell, self.ctl))
        self.append(QryLpShape(self.cell, self.ctl))
        self.append(QryCtlCellSizePos(cell=self.cell, ctl=self.ctl, merged=True))
