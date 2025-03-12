# region imports
from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import uno

from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.exceptions import ex as mEx  # noqa: N812

# region BreakManager
# from ___lo_pip___.debug.break_mgr import BreakMgr

# break_mgr = BreakMgr()
# break_mgr.add_breakpoint("pythonpath.libre_pythonista_lib.code.mod_helper.lp_mod.lp")
# endregion BreakManager

from ...cell.cell_mgr import CellMgr
from ...data.pandas_data_obj import PandasDataObj
from .lp_rules.lp_rules_engine import LpRulesEngine
from .lp_enum import LpEnum

LAST_LP_RESULT = DotDict(data=None)

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCellRange
    from com.sun.star.sheet import SheetCell
    from ...log.log_inst import LogInst
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger

    CURRENT_CELL_OBJ: CellObj
else:
    CURRENT_CELL_OBJ = None
    from libre_pythonista_lib.log.log_inst import LogInst

    SheetCell = Any

# endregion imports

_RULES_ENGINE = LpRulesEngine()


def _collapse_to_used(sheet: CalcSheet, rng_obj: RangeObj) -> RangeObj:
    rng = sheet.get_range(range_obj=rng_obj)
    try:
        found = rng.find_used_range()
        return found.range_obj.copy()
    except mEx.CellRangeError:
        return rng_obj


def _set_last_lp_result(result: Any, **kwargs) -> Any:  # noqa: ANN003, ANN401
    global LAST_LP_RESULT
    log = LogInst()
    dd = DotDict(**kwargs)
    dd.data = result
    LAST_LP_RESULT = dd
    if log.is_debug:
        with log.indent(True):
            log.debug(
                "lp_mod - _set_last_lp_result() - LAST_LP_RESULT.data Type: %s",
                type(LAST_LP_RESULT.data).__name__,
            )
    return LAST_LP_RESULT.data


def _handle_cell_only(addr: str, log: OxtLogger, **kwargs) -> Any:  # noqa: ANN003, ANN401
    global CURRENT_CELL_OBJ
    log.debug("_handle_cell_only() Entered")
    log.debug("lp - Cell Name: %s", addr)
    gbl_cell = cast(CellObj, CURRENT_CELL_OBJ)
    doc = cast(CalcDoc, Lo.current_doc)
    cm = CellMgr(doc)  # singleton
    cell_obj = CellObj.from_cell(addr)
    cell_obj.set_sheet_index(gbl_cell.sheet_idx)
    sheet = doc.sheets[gbl_cell.sheet_idx]
    cell = sheet[cell_obj]

    if cm.has_cell(cell_obj=cell.cell_obj):
        log.debug("lp - Cell found in cache: %s for sheet: %i", cell.cell_obj, cell.cell_obj.sheet_idx)
        py_src = cm.get_py_src(cell_obj=cell.cell_obj)
        return _set_last_lp_result(py_src.value)
    log.debug("lp - Cell not found in cache: %s for sheet: %i", cell.cell_obj, cell.cell_obj.sheet_idx)
    log.debug("Returning actual cell value")
    return _set_last_lp_result(cell.value)


def _handle_sheet_cell(addr: str, log: OxtLogger, **kwargs) -> Any:  # noqa: ANN003, ANN401
    log.debug("_handle_sheet_cell() Entered")
    log.debug("lp - Cell Name: %s", addr)
    doc = cast(CalcDoc, Lo.current_doc)
    sheet_name, addr_str = addr.split(".")
    calc_sheet = doc.sheets.get_by_name(sheet_name)

    cm = CellMgr(doc)  # singleton
    cell_obj = CellObj.from_cell(addr_str)
    cell_obj.set_sheet_index(calc_sheet.sheet_index)
    sheet = doc.sheets[cell_obj.sheet_idx]
    cell = sheet[cell_obj]

    if cm.has_cell(cell_obj=cell.cell_obj):
        log.debug("lp - Cell found in cache: %s for sheet: %i", cell.cell_obj, cell.cell_obj.sheet_idx)
        py_src = cm.get_py_src(cell_obj=cell.cell_obj)
        return _set_last_lp_result(py_src.value)
    log.debug("lp - Cell not found in cache: %s for sheet: %i", cell.cell_obj, cell.cell_obj.sheet_idx)
    log.debug("Returning actual cell value")
    return _set_last_lp_result(cell.value)


def _handle_range_only(addr: str, log: OxtLogger, **kwargs) -> Any:  # noqa: ANN003, ANN401
    global CURRENT_CELL_OBJ
    log.debug("_handle_range_only() Entered")
    log.debug("lp - Cell Name: %s", addr)
    collapse = False
    try:
        collapse = bool(kwargs.get("collapse", False))
    except Exception as e:
        log.warning("collapse parameter must be a boolean value. Using False.")
        collapse = False

    column_types = kwargs.get("column_types")

    gbl_cell = cast(CellObj, CURRENT_CELL_OBJ)

    addr_rng = RangeObj.from_range(addr)
    addr_rng.set_sheet_index(gbl_cell.sheet_idx)
    log.debug("lp - addr_rng: %s", addr_rng)

    doc = cast(CalcDoc, Lo.current_doc)
    sheet = doc.sheets[addr_rng.sheet_idx]
    if collapse:
        addr_rng = _collapse_to_used(sheet, addr_rng)
        log.debug("lp - Collapsed addr_rng: %s", addr_rng)
    cr = sheet.get_range(range_obj=addr_rng)
    pdo = PandasDataObj(cell_rng=cr, col_types=column_types)
    df = pdo.get_data_frame()
    return _set_last_lp_result(df, headers=pdo.has_headers, range_obj=addr_rng)


def _handle_sheet_range_only(addr: str, log: OxtLogger, **kwargs) -> Any:  # noqa: ANN003, ANN401
    log.debug("_handle_sheet_range_only() Entered")
    log.debug("lp - Cell Name: %s", addr)
    collapse = False
    try:
        collapse = bool(kwargs.get("collapse", False))
    except Exception as e:
        log.warning("collapse parameter must be a boolean value. Using False.")
        collapse = False

    column_types = kwargs.get("column_types")

    doc = cast(CalcDoc, Lo.current_doc)
    sheet_name, addr_str = addr.split(".")
    sheet = doc.sheets.get_by_name(sheet_name)

    if doc.range_converter.is_cell_range_name(addr_str):
        addr_rng = RangeObj.from_range(addr_str)
    else:
        # if the range is actually a cell range then handle it as a cell
        return _handle_sheet_cell(addr, log, **kwargs)

    addr_rng.set_sheet_index(sheet.sheet_index)
    log.debug("lp - addr_rng: %s", addr_rng)

    if collapse:
        addr_rng = _collapse_to_used(sheet, addr_rng)
        log.debug("lp - Collapsed addr_rng: %s", addr_rng)
    cr = sheet.get_range(range_obj=addr_rng)
    pdo = PandasDataObj(cell_rng=cr, col_types=column_types)
    df = pdo.get_data_frame()
    return _set_last_lp_result(df, headers=pdo.has_headers, range_obj=addr_rng)


def _handle_named_range_only(addr: str, log: OxtLogger, **kwargs) -> Any:  # noqa: ANN003, ANN401
    log.debug("_handle_named_range_only() Entered")
    global CURRENT_CELL_OBJ
    log.debug("lp - Cell Name: %s", addr)
    gbl_cell = cast(CellObj, CURRENT_CELL_OBJ)
    doc = cast(CalcDoc, Lo.current_doc)
    data_name = addr
    sheet = doc.sheets[gbl_cell.sheet_idx]

    if log.is_debug:
        names = sheet.named_ranges.get_element_names()
        log.debug("lp - Sheet Named Ranges: %s", names)

        names = doc.named_ranges.get_element_names()
        log.debug("lp - Doc Named Ranges: %s", names)

    if sheet.named_ranges.has_by_name(data_name):
        log.debug("lp - Named range found in sheet Name Ranges: %s", data_name)
        nc = sheet.named_ranges.get_by_name(data_name)
    elif doc.named_ranges.has_by_name(data_name):
        log.debug("lp - Named range found in doc Named Ranges: %s", data_name)
        nc = doc.named_ranges.get_by_name(data_name)
        # try to get the current sheet from the named range
    elif doc.database_ranges.has_by_name(data_name):
        log.debug("lp - Named range found in doc Database Ranges: %s", data_name)
        nc = doc.database_ranges.get_by_name(data_name)
    else:
        log.error("lp - Named range %s not found in sheet or document.", data_name)
        return _set_last_lp_result(None)

    cell_range = cast("SheetCellRange", nc.get_referred_cells())
    rng_addr = cell_range.AbsoluteName.replace("$", "")
    if doc.range_converter.is_cell_range_name(rng_addr):
        # range return a DataFrame
        return _handle_sheet_range_only(rng_addr, log, **kwargs)
    else:
        # single cell. return the cell value
        return _handle_sheet_cell(rng_addr, log, **kwargs)


def _handle_sheet_named_range_only(addr: str, log: OxtLogger, **kwargs) -> Any:  # noqa: ANN003, ANN401
    log.debug("_handle_sheet_named_range_only() Entered")
    log.debug("lp - Cell Name: %s", addr)
    doc = cast(CalcDoc, Lo.current_doc)
    sheet_name, data_name = addr.split(".")
    sheet = doc.sheets.get_by_name(sheet_name)

    if log.is_debug:
        names = sheet.named_ranges.get_element_names()
        log.debug("lp - Sheet Named Ranges: %s", names)

        names = doc.named_ranges.get_element_names()
        log.debug("lp - Doc Named Ranges: %s", names)

    if sheet.named_ranges.has_by_name(data_name):
        log.debug("lp - Named range found in sheet Name Ranges: %s", data_name)
        nc = sheet.named_ranges.get_by_name(data_name)
    elif doc.named_ranges.has_by_name(data_name):
        log.debug("lp - Named range found in doc Named Ranges: %s", data_name)
        nc = doc.named_ranges.get_by_name(data_name)
        # try to get the current sheet from the named range
    elif doc.database_ranges.has_by_name(data_name):
        log.debug("lp - Named range found in doc Database Ranges: %s", data_name)
        nc = doc.database_ranges.get_by_name(data_name)
    else:
        log.error("lp - Named range %s not found in sheet or document.", data_name)
        return _set_last_lp_result(None)

    cell_range = cast("SheetCellRange", nc.get_referred_cells())
    rng_addr = cell_range.AbsoluteName.replace("$", "")
    if doc.range_converter.is_cell_range_name(rng_addr):
        # range return a DataFrame
        return _handle_sheet_range_only(rng_addr, log, **kwargs)
    else:
        # single cell. return the cell value
        return _handle_sheet_cell(rng_addr, log, **kwargs)


def lp(addr: str, **kwargs: Any) -> Any:  # noqa: ANN401
    global CURRENT_CELL_OBJ, _RULES_ENGINE
    # break_mgr.check_breakpoint("pythonpath.libre_pythonista_lib.code.mod_helper.lp_mod.lp")
    log = LogInst()
    log.debug("lp - Current Cell Obj Global: %s", CURRENT_CELL_OBJ)
    log.debug("lp - Input Address: %s", addr)
    try:
        if not addr:
            return _set_last_lp_result(None)
        rm = _RULES_ENGINE.get_matched_rule(addr)
        rm_value = rm.get_value()
        log.debug("lp - Rule Matched: %s for %s", rm, addr)
        if rm_value == LpEnum.EMPTY:
            log.debug("lp - Rule found for: %s, Empty", addr)
            return _set_last_lp_result(None)
        if rm_value == LpEnum.CELL_ONLY:
            log.debug("lp - Rule found for: %s, Cell Only", addr)
            return _handle_cell_only(addr, log, **kwargs)

        if rm_value == LpEnum.SHEET_CELL:
            log.debug("lp - Rule found for: %s, Sheet Cell", addr)
            return _handle_sheet_cell(addr, log, **kwargs)

        if rm_value == LpEnum.RNG_ONLY:
            log.debug("lp - Rule found for: %s, Range Only", addr)
            return _handle_range_only(addr, log, **kwargs)
        if rm_value == LpEnum.SHEET_RNG:
            log.debug("lp - Rule found for: %s, Range Only", addr)
            return _handle_sheet_range_only(addr, log, **kwargs)
        if rm_value == LpEnum.NAMED_RNG:
            log.debug("lp - Rule found for: {%s, Named Range Only", addr)
            return _handle_named_range_only(addr, log, **kwargs)
        if rm_value == LpEnum.SHEET_NAMED_RNG:
            log.debug("lp - Rule found for: %s, Sheet Named Range Only", addr)
            return _handle_sheet_named_range_only(addr, log, **kwargs)
        log.debug("lp - Rule not found for: %s", addr)
    except Exception as e:
        log.error("lp - Exception: %s", e, exc_info=True)
        return _set_last_lp_result(None)
