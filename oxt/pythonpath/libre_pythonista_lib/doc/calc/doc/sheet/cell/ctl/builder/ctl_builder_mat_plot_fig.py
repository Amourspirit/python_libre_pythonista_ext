from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_array_ability import CmdArrayAbility
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_control_img_name import CmdControlImgName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_modify_trigger_event import (
        CmdModifyTriggerEvent,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_mat_plot_figure import (
        CmdMatPlotFigure,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_style_text_align import CmdStyleTextAlign
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_mat_plot_figure_img import (
        CmdMatPlotFigureImg,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_storage_location import (
        CmdCtlStorageLocation,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_array_ability import CmdArrayAbility
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_control_img_name import CmdControlImgName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_modify_trigger_event import CmdModifyTriggerEvent
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_rule_name import CmdRuleName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_mat_plot_figure import CmdMatPlotFigure
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_style_text_align import CmdStyleTextAlign
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_mat_plot_figure_img import CmdMatPlotFigureImg
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_storage_location import CmdCtlStorageLocation
    from libre_pythonista_lib.utils.custom_ext import override

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder_mat_plot_figure.py


class CtlBuilderMatPlotFig(CtlBuilder):
    @override
    def append_commands(self) -> None:
        self.append(CmdControlImgName(cell=self.cell, ctl=self.ctl))
        self.append(CmdArrayAbility(cell=self.cell, ctl=self.ctl, ability=False))
        self.append(CmdRuleName(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_MP_FIGURE))
        self.append(CmdModifyTriggerEvent(cell=self.cell, ctl=self.ctl, kind=RuleNameKind.CELL_DATA_TYPE_MP_FIGURE))
        self.append(CmdStyleTextAlign(cell=self.cell, indent=0))
        self.append(CmdCtlStorageLocation(cell=self.cell, ctl=self.ctl))
        self.append(CmdMatPlotFigure(cell=self.cell, ctl=self.ctl, opt=self._get_control_options()))
        self.append(CmdMatPlotFigureImg(cell=self.cell, ctl=self.ctl))
