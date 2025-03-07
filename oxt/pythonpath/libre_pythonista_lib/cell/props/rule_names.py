from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.meta.singleton import Singleton
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.meta.singleton import Singleton
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind


class RuleNames(metaclass=Singleton):
    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        cfg = BasicConfig()
        self._cell_cp_prefix = cfg.cell_cp_prefix
        self._is_init = True

    # region Properties
    @property
    def cell_data_type_simple_ctl(self) -> str:
        """Rule name for cell data type of simple control. This is only used in the SimpleCtl Base Class."""
        return str(RuleNameKind.CELL_DATA_TYPE_SIMPLE_CTL)

    @property
    def cell_data_type_mp_figure(self) -> str:
        """Rule name for cell data type of Matplotlib Figure."""
        return str(RuleNameKind.CELL_DATA_TYPE_MP_FIGURE)

    @property
    def cell_data_type_cell_img(self) -> str:
        """Rule name for cell data type of Cell Images for Plots and stuff."""
        return str(RuleNameKind.CELL_DATA_TYPE_CELL_IMG)

    @property
    def cell_data_type_str(self) -> str:
        """Rule name for cell data type of string."""
        return str(RuleNameKind.CELL_DATA_TYPE_STR)

    @property
    def cell_data_type_none(self) -> str:
        """
        Rule name for cell data type of None.

        This rule is different then Empty because it represents a that did not generate a value.
        """
        return str(RuleNameKind.CELL_DATA_TYPE_NONE)

    @property
    def cell_data_type_empty(self) -> str:
        """
        Rule name for cell data type of Empty.

        This rule is different then None because is represents a cell that has no code entered.
        """
        return str(RuleNameKind.CELL_DATA_TYPE_EMPTY)

    @property
    def cell_data_type_error(self) -> str:
        """Rule name for cell data type of error."""
        return str(RuleNameKind.CELL_DATA_TYPE_ERROR)

    @property
    def cell_data_type_int(self) -> str:
        """Rule name for cell data type of int."""
        return str(RuleNameKind.CELL_DATA_TYPE_INT)

    @property
    def cell_data_type_tbl_data(self) -> str:
        """Rule name for cell data type of 2D."""
        return str(RuleNameKind.CELL_DATA_TYPE_TBL_DATA)

    @property
    def cell_data_type_float(self) -> str:
        """Rule name for cell data type of float."""
        return str(RuleNameKind.CELL_DATA_TYPE_FLOAT)

    @property
    def cell_data_type_pd_df(self) -> str:
        """Rule name for cell data type of pandas DataFrame."""
        return str(RuleNameKind.CELL_DATA_TYPE_PD_DF)

    @property
    def cell_data_type_pd_series(self) -> str:
        """Rule name for cell data type of pandas Series."""
        return str(RuleNameKind.CELL_DATA_TYPE_PD_SERIES)

    # endregion Properties
