from __future__ import annotations
from typing import TYPE_CHECKING, Type, overload

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_float import (
        CtlBuilderFloat,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder_str.py


def _get_control_class(ctl_kind: CtlKind) -> Type[CtlBuilder] | None:
    """
    Gets the control class for the given control kind.

    Args:
        ctl_kind (CtlKind): The kind of control to get the class for

    Returns:
        Type[CtlBase] | None: The control class or None if not found
    """
    # Import controls here to avoid circular imports
    if not TYPE_CHECKING:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_float import CtlBuilderFloat

    control_map = {
        CtlKind.STRING: CtlBuilderStr,
        CtlKind.FLOAT: CtlBuilderFloat,
    }
    return control_map.get(ctl_kind)


@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.STRING]) -> CtlBuilderStr: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.FLOAT]) -> CtlBuilderFloat: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBuilder: ...


def get_builder(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBuilder:
    control_class = _get_control_class(ctl_kind)
    if control_class is None:
        raise ValueError("Invalid control kind")
    builder = control_class(calc_cell)
    return builder
