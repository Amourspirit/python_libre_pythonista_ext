from __future__ import annotations
from typing import TYPE_CHECKING

from ...utils.singleton_base import SingletonBase

if TYPE_CHECKING:
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class RuleNames(SingletonBase):
    # _instance = None

    # def __new__(cls) -> RuleNames:
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._is_init = False
    #     return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        cfg = Config()
        self._cell_cp_prefix = cfg.cell_cp_prefix
        self._is_init = True

    # region Properties
    @property
    def cell_data_type_simple_ctl(self) -> str:
        """Rule name for cell data type of simple control. This is only used in the SimpleCtl Base Class."""
        return "cell_data_type_simple_ctl"

    @property
    def cell_data_type_str(self) -> str:
        """Rule name for cell data type of string."""
        return "cell_data_type_str"

    @property
    def cell_data_type_none(self) -> str:
        """
        Rule name for cell data type of None.

        This rule is different then Empty because it represents a that did not generate a value.
        """
        return "cell_data_type_none"

    @property
    def cell_data_type_empty(self) -> str:
        """
        Rule name for cell data type of Empty.

        This rule is different then None because is represents a cell that has no code entered.
        """
        return "cell_data_type_empty"

    @property
    def cell_data_type_error(self) -> str:
        """Rule name for cell data type of error."""
        return "cell_data_type_error"

    @property
    def cell_data_type_int(self) -> str:
        """Rule name for cell data type of int."""
        return "cell_data_type_int"

    @property
    def cell_data_type_tbl_data(self) -> str:
        """Rule name for cell data type of 2D."""
        return "cell_data_type_tbl_data"

    @property
    def cell_data_type_float(self) -> str:
        """Rule name for cell data type of float."""
        return "cell_data_type_float"

    @property
    def cell_data_type_pd_df(self) -> str:
        """Rule name for cell data type of pandas DataFrame."""
        return "cell_data_type_pd_df"

    @property
    def cell_data_type_pd_series(self) -> str:
        """Rule name for cell data type of pandas Series."""
        return "cell_data_type_pd_series"

    # endregion Properties
