from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcCell
from ..props.key_maker import KeyMaker

from .array_df import ArrayDF
from .array_ds import ArrayDS
from .array_tbl import ArrayTbl

if TYPE_CHECKING:
    from .array_t import ArrayT
else:
    ArrayT = object


def get_array_helper(cell: CalcCell) -> ArrayT | None:
    """
    Gets the Array Helper for the cell.

    Args:
        cell (CalcCell): Calc Cell

    Returns:
        ArrayT | None: Array Helper or None
    """
    km = KeyMaker()

    rule_name = cell.get_custom_property(km.pyc_rule_key, None)
    if rule_name is None:
        return None
    rules = km.rule_names

    if rule_name == rules.cell_data_type_pd_df:
        return ArrayDF(cell)
    if rule_name == rules.cell_data_type_pd_series:
        return ArrayDS(cell)
    if rule_name == rules.cell_data_type_tbl_data:
        return ArrayTbl(cell)
    return None
