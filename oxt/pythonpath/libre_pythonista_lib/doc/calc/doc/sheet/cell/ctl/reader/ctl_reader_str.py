from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.label.qry_lbl_default import QryLblDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_current import QryCtlCurrent
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_modify_trigger_event import (
        QryCtlModifyTriggerEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_orig_rule_name import (
        QryCtlOrigRuleName,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_rule_name import QryCtlRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_style_bg_default import (
        QryCtlStyleBgDefault,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader import CtlReader
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.label.qry_lbl_default import QryLblDefault
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_current import QryCtlCurrent
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_modify_trigger_event import QryCtlModifyTriggerEvent
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_orig_rule_name import QryCtlOrigRuleName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_rule_name import QryCtlRuleName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_style_bg_default import QryCtlStyleBgDefault
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_lp_shape import QryLpShape
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader import CtlReader
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.utils.custom_ext import override

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder_str.py


class CtlReaderStr(CtlReader):
    @override
    def append_query(self) -> None:
        self.append(QryLblDefault(self.cell, self.ctl))
        self.append(QryCtlShapeName(self.cell, self.ctl))
        self.append(QryCtlRuleName(self.cell, self.ctl))
        self.append(QryCtlOrigRuleName(self.cell, self.ctl))
        self.append(QryCtlModifyTriggerEvent(self.cell, self.ctl))
        self.append(QryLpShape(self.cell, self.ctl))
        self.append(QryCtlStyleBgDefault(self.cell, self.ctl))
        self.append(QryCtlCurrent(self.cell, self.ctl))
        self.append(QryCtlCellSizePos(self.cell, self.ctl))

    @override
    def read(self) -> Ctl:
        ctl = super().read()
        ctl.control_kind = CtlKind.STRING
        ctl.ctl_props = (
            CtlPropKind.CTL_SHAPE,
            CtlPropKind.CTL_ORIG,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )
        return ctl
