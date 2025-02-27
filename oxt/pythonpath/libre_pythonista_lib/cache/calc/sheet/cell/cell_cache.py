from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
else:
    from libre_pythonista_lib.doc.doc_globals import MemCache
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache


def _get_cell_cache_key(cell: CalcCell) -> str:
    return f"cell_{hash(cell.cell_obj)}"


def get_cell_cache(cell: CalcCell) -> MemCache:
    """Get cache sheet from cache"""
    sheet_cache = get_sheet_cache(cell.calc_sheet)
    key = _get_cell_cache_key(cell)
    if key not in sheet_cache:
        sheet_cache[key] = MemCache()
    return sheet_cache[key]


def remove_cell_cache(cell: CalcCell) -> None:
    """Remove cache sheet from cache"""
    sheet_cache = get_sheet_cache(cell.calc_sheet)
    key = _get_cell_cache_key(cell)
    if key in sheet_cache:
        del sheet_cache[key]
