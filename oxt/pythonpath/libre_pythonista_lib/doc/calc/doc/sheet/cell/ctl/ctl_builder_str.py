from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_builder import CtlBuilder
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_ctl_shape_name import CmdCtlShapeName

    def override(f) -> object:  # noqa: ANN001
        return f


class CtlBuilderStr(CtlBuilder):
    @override
    def append_commands(self) -> None:
        super().append_commands()
        self.append(CmdCtlShapeName)
