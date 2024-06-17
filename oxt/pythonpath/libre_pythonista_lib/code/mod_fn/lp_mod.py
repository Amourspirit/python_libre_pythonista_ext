from typing import Any, cast, TYPE_CHECKING
import re
from ...cell.cell_mgr import CellMgr

LAST_LP_RESULT = None

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCellRange
    import pandas as pd
    import numpy as np
    from ooodev.calc import CalcDoc
    from ooodev.utils.data_type.cell_obj import CellObj
    from ooodev.utils.data_type.range_obj import RangeObj
    from ...log.log_inst import LogInst

    CURRENT_CELL_OBJ: CellObj
else:
    CURRENT_CELL_OBJ = None
    import pandas as pd
    from ooodev.calc import CalcDoc
    from ooodev.utils.data_type.cell_obj import CellObj
    from ooodev.utils.data_type.range_obj import RangeObj
    from libre_pythonista_lib.log.log_inst import LogInst


def _set_last_lp_result(result: Any) -> Any:
    global LAST_LP_RESULT
    log = LogInst()

    LAST_LP_RESULT = result
    if log.is_debug:
        log.debug(f"lp_mod - _set_last_lp_result() - LAST_LP_RESULT: {LAST_LP_RESULT}")
    return LAST_LP_RESULT


def lp(addr: str, **Kwargs: Any) -> Any:
    global CURRENT_CELL_OBJ
    log = LogInst()
    log.debug(f"lp - Current Cell Obj Global: {CURRENT_CELL_OBJ}")
    if not addr:
        return None
    gbl_cell = cast(CellObj, CURRENT_CELL_OBJ)
    cell_obj = CellObj(col=gbl_cell.col, row=gbl_cell.row, sheet_idx=gbl_cell.sheet_idx)
    doc = CalcDoc.from_current_doc()
    cm = CellMgr(doc)  # singleton
    # also needs to be able to look up the name from named ranges.
    # Also needs to return the cell value if the cell is not a python cell.
    header = Kwargs.get("headers", False)
    addr_rng = None
    sheet_idx = cell_obj.sheet_idx
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
                log.debug(f"lp - Named range found in sheet: {addr}")
                nc = sheet.named_ranges.get_by_name(addr)
            elif doc.named_ranges.has_by_name(addr):
                log.debug(f"lp - Named range found in doc: {addr}")
                nc = doc.named_ranges.get_by_name(addr)
            else:
                log.error(f"lp - Named range {addr} not found in sheet or document.")
                return _set_last_lp_result(None)
            cell_range = cast("SheetCellRange", nc.get_referred_cells())
            addr_rng = RangeObj.from_range(cell_range.getRangeAddress())
            log.debug(f"lp - Name addr_rng: {addr_rng}")

    try:

        if addr_rng is None:
            addr_rng = RangeObj.from_range(addr)
        log.debug(f"lp - addr_rng: {addr_rng}")

        sheet_idx = cell_obj.sheet_idx
        if addr_rng.sheet_idx >= 0:
            sheet_idx = addr_rng.sheet_idx
        sheet = doc.sheets[sheet_idx]
        data = sheet.get_array(range_obj=addr_rng)
        if header:
            data_len = len(data)
            if data_len == 0:
                df = pd.DataFrame()
            elif data_len == 1:
                df = pd.DataFrame([], columns=data[0])
            else:
                df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame(data)

        return _set_last_lp_result(df)
    except Exception as e:
        log.error(f"lp - Exception: {e}", exc_info=True)
        return _set_last_lp_result(None)
