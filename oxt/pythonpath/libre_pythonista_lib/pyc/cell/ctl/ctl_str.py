from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.loader import Lo

from .ctl_kind import CtlKind
from .ctl_prop_kind import CtlPropKind
from .mixin.ctl_kind_mixin import CtlKindMixin
from .mixin.calc_cell_mixin import CalcCellMixin
from .mixin.ctl_namer_mixin import CtlNamerMixin

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.res.res_resolver_mixin import ResResolverMixin
    from ....log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.res.res_resolver_mixin import ResResolverMixin
    from libre_pythonista_lib.log.log_mixin import LogMixin


class CtlStr(EventsPartial, LogMixin, CalcCellMixin, CtlKindMixin, CtlNamerMixin, ResResolverMixin):
    def __init__(self, calc_cell: CalcCell) -> None:
        EventsPartial.__init__(self)
        LogMixin.__init__(self)
        CalcCellMixin.__init__(self, calc_cell)
        CtlKindMixin.__init__(self)
        CtlNamerMixin.__init__(self, calc_cell)
        ResResolverMixin.__init__(self, Lo.get_context())

    # region Methods
    def get_label(self) -> str:
        return "<>"

    # region CtlKindMixin overrides
    @override
    def _get_ctl_props(self) -> Tuple[CtlPropKind, ...]:
        """Gets the control properties."""
        return (
            CtlPropKind.CTL_SHAPE,
            CtlPropKind.CTL_ORIG,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )

    @override
    def _get_control_kind(self) -> CtlKind:
        """Gets the control kind."""
        return CtlKind.STRING

    # endregion CtlKindMixin overrides

    # endregion Methods

    # region Properties

    # endregion Properties
