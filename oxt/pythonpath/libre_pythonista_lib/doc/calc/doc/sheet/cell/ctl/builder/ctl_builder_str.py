from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_array_ability import CmdArrayAbility
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_modify_trigger_event import (
        CmdModifyTriggerEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_orig_rule_name import CmdOrigRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_str import CmdStr
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.label.cmd_lbl_default import CmdLblDefault
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_array_ability import CmdArrayAbility
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_modify_trigger_event import CmdModifyTriggerEvent
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_orig_rule_name import CmdOrigRuleName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_str import CmdStr
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.label.cmd_lbl_default import CmdLblDefault
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.utils.custom_ext import override


class CtlBuilderStr(CtlBuilder):
    @override
    def append_commands(self) -> None:
        self.append(CmdLblDefault(cell=self.cell, ctl=self.ctl))
        self.append(CmdCtlShapeName(self.cell, self.ctl))
        self.append(CmdRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_STR))
        self.append(CmdOrigRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_STR))
        self.append(CmdArrayAbility(cell=self.cell, ctl=self.ctl, ability=False))
        self.append(CmdModifyTriggerEvent(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_STR))
        self.append(CmdStr(cell=self.cell, ctl=self.ctl))

    @override
    def build(self) -> Ctl:
        ctl = super().build()
        ctl.control_kind = CtlKind.STRING
        ctl.ctl_props = (
            CtlPropKind.CTL_SHAPE,
            CtlPropKind.CTL_ORIG,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )
        return ctl
