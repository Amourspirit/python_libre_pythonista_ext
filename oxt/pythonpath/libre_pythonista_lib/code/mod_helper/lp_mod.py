from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import re
import uno

from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.exceptions import ex as mEx
from ...cell.cell_mgr import CellMgr
from ...data.pandas_data_obj import PandasDataObj

LAST_LP_RESULT = DotDict(data=None)

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCellRange
    from com.sun.star.sheet import SheetCell
    from ...log.log_inst import LogInst

    CURRENT_CELL_OBJ: CellObj
else:
    CURRENT_CELL_OBJ = None
    from libre_pythonista_lib.log.log_inst import LogInst

    SheetCell = Any


def _set_last_lp_result(result: Any, **kwargs) -> Any:
    global LAST_LP_RESULT
    log = LogInst()
    dd = DotDict(**kwargs)
    dd.data = result
    LAST_LP_RESULT = dd
    if log.is_debug:
        with log.indent(True):
            log.debug(
                f"lp_mod - _set_last_lp_result() - LAST_LP_RESULT.data Type: {type(LAST_LP_RESULT.data).__name__}"
            )
    return LAST_LP_RESULT.data


def _get_addr(addr: str) -> str:
    if not addr:
        return ""
    if ":" in addr:
        # check to see if this is a single cell or a range
        parts = addr.split(":")
        if parts[0].upper() == parts[1].upper():
            return parts[0].upper()
        else:
            return f"{parts[0].upper()}:{parts[1].upper()}"
    return addr.upper()


def _collapse_to_used(sheet: CalcSheet, rng_obj: RangeObj) -> RangeObj:
    rng = sheet.get_range(range_obj=rng_obj)
    try:
        found = rng.find_used_range()
        return found.range_obj.copy()
    except mEx.CellRangeError:
        return rng_obj


def lp(addr: str, **kwargs: Any) -> Any:
    global CURRENT_CELL_OBJ
    log = LogInst()
    with log.indent(True):
        log.debug(f"lp - Current Cell Obj Global: {CURRENT_CELL_OBJ}")
        addr = _get_addr(addr)
        is_debug = log.is_debug
        if is_debug:
            log.debug(f"lp - Address: {addr}")
        if not addr:
            return _set_last_lp_result(None)
        try:
            gbl_cell = cast(CellObj, CURRENT_CELL_OBJ)
            cell_obj = CellObj(col=gbl_cell.col, row=gbl_cell.row, sheet_idx=gbl_cell.sheet_idx)
            if is_debug:
                log.debug(f"lp - Cell Obj: {cell_obj}")
            doc = cast(CalcDoc, Lo.current_doc)
            # doc = CalcDoc.from_current_doc()
            if is_debug:
                log.debug(f"lp - CalcDoc Runtime ID: {doc.runtime_uid}")
            cm = CellMgr(doc)  # singleton
            log.debug("lp - Got CellMgr")
            # also needs to be able to look up the name from named ranges.
            # Also needs to return the cell value if the cell is not a python cell.
            # headers = kwargs.get("headers", False)
        except Exception:
            log.exception("lp - Could not get CalcDoc or CellMgr instance.")
            return _set_last_lp_result(None)
        collapse = False
        try:
            collapse = bool(kwargs.get("collapse", False))
        except Exception as e:
            log.warning("collapse parameter must be a boolean value. Using False.")
            collapse = False
        addr_rng = None
        sheet_idx = cell_obj.sheet_idx
        log.debug(f"lp - Sheet Index: {sheet_idx}")
        log.debug(f"lp - Address: {addr}")
        if not ":" in addr:
            # could be a cell or a named range
            # create a regular expression that can detect if it is a cell or a named range
            # https://www.libreofficehelp.com/maximum-number-rows-columns-cells-libreoffice-calc/
            # Maximum number of Columns per worksheet = 16384 (Col A to XFD).
            cell_name_regex = r"^[A-Za-z]{1,3}\d{1,7}$"
            sheet_cell_name_regex = r"^[A-Za-z\s\d]+\.[A-Za-z]{1,3}\d{1,7}$"
            is_cell_name = bool(re.match(cell_name_regex, addr))
            if not is_cell_name:
                is_cell_name = bool(re.match(sheet_cell_name_regex, addr))
            if is_cell_name:
                log.debug(f"lp - Cell Name: {addr}")
                addr_cell = CellObj.from_cell(addr)
                if addr_cell.sheet_idx >= 0:
                    sheet_idx = addr_cell.sheet_idx
                sheet = doc.sheets[sheet_idx]
                cell = sheet[addr_cell]
                if cm.has_cell(cell_obj=cell.cell_obj):
                    log.debug(f"lp - Cell found in cache: {cell.cell_obj} for sheet: {cell.cell_obj.sheet_idx}")
                    py_src = cm.get_py_src(cell_obj=cell.cell_obj)
                    return _set_last_lp_result(py_src.value)
                log.debug(f"lp - Cell not found in cache: {cell.cell_obj} for sheet: {cell.cell_obj.sheet_idx}")
                log.debug("Returning actual cell value")
                return _set_last_lp_result(cell.value)
            else:
                # named range
                # return the range
                log.debug(f"lp - Cell Named Range: {addr}")
                sheet = doc.sheets[sheet_idx]
                if log.is_debug:
                    names = sheet.named_ranges.get_element_names()
                    log.debug(f"lp - Sheet Named Ranges: {names}")

                    names = doc.named_ranges.get_element_names()
                    log.debug(f"lp - Doc Named Ranges: {names}")

                if sheet.named_ranges.has_by_name(addr):
                    log.debug(f"lp - Named range found in sheet Name Ranges: {addr}")
                    nc = sheet.named_ranges.get_by_name(addr)
                elif doc.named_ranges.has_by_name(addr):
                    log.debug(f"lp - Named range found in doc Named Ranges: {addr}")
                    nc = doc.named_ranges.get_by_name(addr)
                elif doc.database_ranges.has_by_name(addr):
                    log.debug(f"lp - Named range found in doc Database Ranges: {addr}")
                    nc = doc.database_ranges.get_by_name(addr)
                else:
                    log.error(f"lp - Named range {addr} not found in sheet or document.")
                    return _set_last_lp_result(None)
                cell_range = cast("SheetCellRange", nc.get_referred_cells())
                addr_rng = RangeObj.from_range(cell_range.getRangeAddress())
                log.debug(f"lp - Name addr_rng: {addr_rng}")

        try:

            column_types = kwargs.get("column_types", None)

            if addr_rng is None:
                addr_rng = RangeObj.from_range(addr)
            log.debug(f"lp - addr_rng: {addr_rng}")

            sheet_idx = cell_obj.sheet_idx
            sheet = doc.sheets[sheet_idx]
            if collapse:
                addr_rng = _collapse_to_used(sheet, addr_rng)
                log.debug(f"lp - Collapsed addr_rng: {addr_rng}")
            if addr_rng.sheet_idx >= 0:
                sheet_idx = addr_rng.sheet_idx
            cr = sheet.get_range(range_obj=addr_rng)
            pdo = PandasDataObj(cell_rng=cr, col_types=column_types)
            df = pdo.get_data_frame()
            return _set_last_lp_result(df, headers=pdo.has_headers, range_obj=addr_rng)

        except Exception as e:
            log.error(f"lp - Exception: {e}", exc_info=True)
            return _set_last_lp_result(None)
