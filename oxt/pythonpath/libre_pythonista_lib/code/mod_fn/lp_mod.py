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


def lp(addr: str, **Kwargs: Any) -> Any:
    global CURRENT_CELL_OBJ, LAST_LP_RESULT
    log = LogInst()
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
        is_cell_name = bool(re.match(cell_name_regex, addr))
        if is_cell_name:
            log.debug(f"lp - Cell Name: {addr}")
            addr_cell = CellObj.from_cell(addr)
            if addr_cell.sheet_idx >= 0:
                sheet_idx = addr_cell.sheet_idx
            sheet = doc.sheets[sheet_idx]
            cell = sheet[addr_cell]
            if cm.has_cell(cell_obj=cell.cell_obj):
                log.debug(f"lp - Cell found in cache: {addr}")
                py_src = cm.get_py_src(cell_obj=cell.cell_obj)
                return py_src.value
            log.debug(f"lp - Cell not found in cache: {addr}")
            log.debug("Returning actual cell value")
            LAST_LP_RESULT = cell.value
            return LAST_LP_RESULT
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
                LAST_LP_RESULT = None
                return None
            cell_range = cast("SheetCellRange", nc.get_referred_cells())
            addr_rng = RangeObj.from_range(cell_range.getRangeAddress())
            log.debug(f"lp - Name addr_rng: {addr_rng}")

    if addr_rng is None:
        addr_rng = RangeObj.from_range(addr)
    log.debug(f"lp - addr_rng: {addr_rng}")

    sheet_idx = cell_obj.sheet_idx
    if addr_rng.sheet_idx >= 0:
        sheet_idx = addr_rng.sheet_idx
    sheet = doc.sheets[sheet_idx]
    data = sheet.get_array(range_obj=addr_rng)
    # range

    header = Kwargs.get("headers", False)
    LAST_LP_RESULT = pd.DataFrame(data)
    return LAST_LP_RESULT
    # Convert the DataFrame to a record array, then to a tuple
    # this should be return to the function as an object.
    # the function needs to be responsible for converting it from object to a record array
    data_tuple = tuple(df.itertuples(index=False, name=None))
    log.debug(f"data\n{data_tuple}")
    return data_tuple
