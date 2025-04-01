from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_array_ability import CmdArrayAbility
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_control_name import CmdControlName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_modify_trigger_event import (
        CmdModifyTriggerEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_orig_rule_name import CmdOrigRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_empty import CmdEmpty
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.label.cmd_lbl_default import CmdLblDefault
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_style_text_align import CmdStyleTextAlign
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_array_ability import CmdArrayAbility
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_control_name import CmdControlName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_modify_trigger_event import CmdModifyTriggerEvent
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_orig_rule_name import CmdOrigRuleName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_empty import CmdEmpty
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.label.cmd_lbl_default import CmdLblDefault
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_style_text_align import CmdStyleTextAlign
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.utils.custom_ext import override

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder.py


class CtlBuilderEmpty(CtlBuilder):
    @override
    def append_commands(self) -> None:
        self.append(CmdLblDefault(cell=self.cell, ctl=self.ctl))
        self.append(CmdControlName(cell=self.cell, ctl=self.ctl))
        self.append(CmdCtlShapeName(self.cell, self.ctl))
        self.append(CmdRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_EMPTY))
        self.append(CmdOrigRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_EMPTY))
        self.append(CmdArrayAbility(cell=self.cell, ctl=self.ctl, ability=False))
        self.append(CmdModifyTriggerEvent(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_EMPTY))
        self.append(CmdEmpty(cell=self.cell, ctl=self.ctl, opt=self._get_control_options()))
        self.append(CmdStyleTextAlign(cell=self.cell))
