from __future__ import annotations
from typing import Tuple, TYPE_CHECKING, Set, Union


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.mixin.calc_cell_mixin import CalcCellMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.feature_kind import FeatureKind
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.mixin.calc_cell_mixin import CalcCellMixin
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.feature_kind import FeatureKind


class CtlBase(LogMixin, CalcCellMixin):
    def __init__(self, ctl: Ctl) -> None:
        LogMixin.__init__(self)
        CalcCellMixin.__init__(self, ctl.cell)
        self._ctl = ctl
        self.__ctl_kind = None

    def get_supports_prop(self, prop: CtlPropKind) -> bool:
        """Checks if the control supports the given property."""
        if not self.ctl_props:
            return False
        return prop in self.ctl_props

    def get_supports_feature(self, feature: FeatureKind) -> bool:
        """Checks if the feature is supported."""
        if not self.supported_features:
            return False
        return feature in self.supported_features

    def get_shape_name(self) -> Union[str, None]:
        """
        Gets the control shape name.

        For controls that do not have a shape name, this method will return None.

        Returns:
            str, None: The control shape name or None if not found.
        """
        return self.ctl.ctl_shape_name

    def __eq__(self, other: object) -> bool:
        """
        Compares the control kind of this object with another object.

        Equality is determined by comparing the control kind of the two objects.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the control kind of this object is equal to the control kind of the other object, False otherwise.
        """
        if isinstance(other, CtlBase):
            return self.control_kind == other.control_kind
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(Ctl)>"

    # region Properties
    @property
    def ctl(self) -> Ctl:
        return self._ctl

    @property
    def array_ability(self) -> bool:
        return self.ctl.array_ability

    @property
    def control_kind(self) -> CtlKind:
        """Gets the control kind."""
        return self.ctl.control_kind

    @property
    def ctl_props(self) -> Tuple[CtlPropKind, ...]:
        """Gets the control properties."""
        return self.ctl.ctl_props

    @property
    def supported_features(self) -> Set[FeatureKind]:
        return self.ctl.supported_features

    @property
    def code_name(self) -> str:
        return self.ctl.ctl_code_name

    @property
    def addr(self) -> str:
        return self.ctl.addr

    @property
    def modify_trigger_event(self) -> RuleNameKind:
        return self.ctl.modify_trigger_event

    @property
    def rule_kind(self) -> RuleNameKind:
        return self.ctl.ctl_rule_kind

    @property
    def orig_rule_kind(self) -> RuleNameKind:
        return self.ctl.ctl_orig_rule_kind

    @property
    def ctl_kind(self) -> CtlKind:
        """Gets the control kind."""
        if self.__ctl_kind is None:
            self.__ctl_kind = CtlKind.from_rule_name_kind(self.rule_kind)
        return self.__ctl_kind

    # endregion Properties
