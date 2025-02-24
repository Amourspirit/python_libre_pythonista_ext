from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_orig_rule_name import CmdOrigRuleName
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_builder import CtlBuilder
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
    from libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_orig_rule_name import CmdOrigRuleName

    def override(f) -> object:  # noqa: ANN001
        return f


class CtlBuilderStr(CtlBuilder):
    @override
    def append_commands(self) -> None:
        super().append_commands()
        self.append(CmdCtlShapeName(self.cell, self.ctl))
        self.append(CmdRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_STR))
        self.append(CmdOrigRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_STR))
