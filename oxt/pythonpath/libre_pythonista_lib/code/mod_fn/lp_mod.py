from typing import Any, cast, TYPE_CHECKING


if TYPE_CHECKING:
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
    global CURRENT_CELL_OBJ
    log = LogInst()
    if not addr:
        return None
    gbl_cell = cast(CellObj, CURRENT_CELL_OBJ)
    cell_obj = CellObj(col=gbl_cell.col, row=gbl_cell.row, sheet_idx=gbl_cell.sheet_idx)
    doc = CalcDoc.from_current_doc()
    if not ":" in addr:
        addr_cell = CellObj.from_cell(addr)
        sheet_idx = cell_obj.sheet_idx
        if addr_cell.sheet_idx >= 0:
            sheet_idx = addr_cell.sheet_idx
        sheet = doc.sheets[sheet_idx]
        cell = sheet[addr_cell]
        # return cell.component.getString()
        # return cell.component.getValue()
        return cell.value
    else:
        addr_rng = RangeObj.from_range(addr)
        log.debug(f"lp - addr_rng: {addr_rng}")

        sheet_idx = cell_obj.sheet_idx
        if addr_rng.sheet_idx >= 0:
            sheet_idx = addr_rng.sheet_idx
        sheet = doc.sheets[sheet_idx]
        data = sheet.get_array(range_obj=addr_rng)
        # range

        header = Kwargs.get("headers", False)
        df = pd.DataFrame(data)
        return df
        # Convert the DataFrame to a record array, then to a tuple
        # this should be return to the function as an object.
        # the function needs to be responsible for converting it from object to a record array
        data_tuple = tuple(df.itertuples(index=False, name=None))
        log.debug(f"data\n{data_tuple}")
        return data_tuple
