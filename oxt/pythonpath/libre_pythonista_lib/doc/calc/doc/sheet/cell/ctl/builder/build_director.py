from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr


def get_builder(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBuilder:
    if ctl_kind == CtlKind.STRING:
        builder = CtlBuilderStr(calc_cell)
        return builder
    raise ValueError("Invalid control kind")
