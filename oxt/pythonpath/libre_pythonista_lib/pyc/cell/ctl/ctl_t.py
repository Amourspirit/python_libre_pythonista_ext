from __future__ import annotations
from typing import Protocol, Tuple
from ooodev.calc import CalcCell
from .ctl_prop_kind import CtlPropKind
from .ctl_kind import CtlKind


class CtlT(Protocol):
    def __init__(self, calc_cell: CalcCell) -> None: ...

    def get_label(self) -> str:
        """Gets the control label such as ``<>``."""
        ...

    def supports_prop(self, prop: CtlPropKind) -> bool:
        """Checks if the control supports the given property."""
        ...

    @property
    def calc_cell(self) -> CalcCell: ...

    @calc_cell.setter
    def calc_cell(self, value: CalcCell) -> None: ...

    @property
    def control_kind(self) -> CtlKind:
        """Gets the control kind."""
        ...

    @property
    def ctl_props(self) -> Tuple[CtlPropKind, ...]:
        """Gets the control properties."""
        ...

    @property
    def ctl_name(self) -> str: ...

    @property
    def ctl_shape_name(self) -> str: ...

    @property
    def code_name(self) -> str: ...
