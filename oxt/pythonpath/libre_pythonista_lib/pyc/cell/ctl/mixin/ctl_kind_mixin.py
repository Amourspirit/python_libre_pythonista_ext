from __future__ import annotations
from typing import Tuple
from ..ctl_kind import CtlKind
from ..ctl_prop_kind import CtlPropKind


class CtlKindMixin:
    def __init__(self) -> None:
        self.__control_kind = self._get_control_kind()
        self.__ctl_props = self._get_ctl_props()

    # region Methods
    def _get_ctl_props(self) -> Tuple[CtlPropKind, ...]:
        """Gets the control properties."""
        raise NotImplementedError

    def _get_control_kind(self) -> CtlKind:
        """Gets the control kind."""
        raise NotImplementedError

    def supports_prop(self, prop: CtlPropKind) -> bool:
        """Checks if the control supports the given property."""
        return prop in self.ctl_props

    # endregion Methods

    # region Properties
    @property
    def control_kind(self) -> CtlKind:
        """Gets the control kind."""
        return self.__control_kind

    @property
    def ctl_props(self) -> Tuple[CtlPropKind, ...]:
        """Gets the control properties."""
        return self.__ctl_props

    # endregion Properties
