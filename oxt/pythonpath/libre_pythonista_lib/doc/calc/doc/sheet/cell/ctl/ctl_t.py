from __future__ import annotations
from typing import Protocol, Tuple, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind


class CtlT(Protocol):
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
