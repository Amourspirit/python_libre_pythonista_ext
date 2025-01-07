from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple
from pathlib import Path
from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.loader.inst.options import Options
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.table_helper import TableHelper
from ooodev.utils import gen_util
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_src_manager_simple(loader) -> None:
    """
    This test is testing the source manager in a simple way.

    When ever a cells python code is updated, the on_cell() callback is called.
    The callback will update the cell with the result of the python code.

    When a cell is updated, all cells that come after it will also be updated.

    The source code for the sheet is treated as a single module.
    This means when a previous cell get updated then all other cells that were using its vars will also be updated.
    """
    if TYPE_CHECKING:
        from build.pythonpath.libre_pythonista_lib.code import py_source_mgr
        from build.pythonpath.libre_pythonista_lib.code import cell_cache
    else:
        # import libre_pythonista_lib
        # import libre_pythonista
        from libre_pythonista_lib.code import py_source_mgr
        from libre_pythonista_lib.code import cell_cache

    def on_cell(src: Any, event_args: EventArgs) -> None:  # noqa: ANN401
        ed = cast(DotDict, event_args.event_data)
        if ed.result is not None:
            doc = cast(CalcDoc, ed.doc)
            sheet = doc.sheets[ed.sheet_idx]
            address = (ed.col, ed.row)
            sheet[address].value = ed.result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet["A1"]
        cell.value = 1
        cell_cache.CellCache.reset_instance(doc)
        mgr = py_source_mgr.PySourceManager(doc)
        mgr.subscribe_after_source_update(cb=on_cell)
        mgr.add_source("print('Hello World!')\nx = 22", cell=cell.cell_obj)
        cell = sheet[cell.cell_obj]
        assert cell.value == 22
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 22

        cell = sheet["A2"]
        mgr.add_source("y = x + 10", cell=cell.cell_obj)
        assert cell.value == 32
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 32

        cell = sheet["A3"]
        mgr.add_source("z = y + 10", cell=cell.cell_obj)
        assert cell.value == 42
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 42

        cell = sheet["A4"]
        mgr.add_source("aa = 'Nice!'", cell=cell.cell_obj)
        assert cell.value == "Nice!"
        py_src = mgr[cell.cell_obj]
        assert py_src.value == "Nice!"

        cell = sheet["A2"]
        mgr.update_source("y = 223", cell=cell.cell_obj)
        assert cell.value == 223
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 223

        # now that cell (0, 1), A2, is update to 223, A3 should be 233
        cell = sheet["A3"]
        assert cell.value == 233
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 233

        cell = sheet["A4"]
        assert cell.value == "Nice!"

    finally:
        if doc is not None:
            doc.close()


def test_src_manager_across_down(loader, tmp_path) -> None:  # noqa: ANN001
    """
    This test is writing rows and columns into the sheet.
    Each cell is a code cell that has a value of the previous cell + 1.

    The ``on_cell()`` callback will update the cell with the result of the python code as the sheet python module is being updated.

    A test is run on each cell to confirm that the value is correct.

    The document is saved and then reloaded.
    Once reloaded the python code is run and updates the values again.
    A final test is run to confirm that the values are correct.
    """
    if TYPE_CHECKING:
        from build.pythonpath.libre_pythonista_lib.code import py_source_mgr
        from build.pythonpath.libre_pythonista_lib.code import cell_cache
    else:
        from libre_pythonista_lib.code import py_source_mgr
        from libre_pythonista_lib.code import cell_cache

    def on_cell(src: Any, event_args: EventArgs) -> None:  # noqa: ANN401
        ed = cast(DotDict, event_args.event_data)
        if ed.result is not None:
            doc = cast(CalcDoc, ed.doc)
            sheet = doc.sheets[ed.sheet_idx]
            address = (ed.col, ed.row)
            sheet[address].value = ed.result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        sheet_idx = sheet.sheet_index
        cell_cache.CellCache.reset_instance(doc)
        mgr = py_source_mgr.PySourceManager(doc)
        mgr.subscribe_after_source_update(cb=on_cell)

        cols = 3
        rows = 4
        for j in range(rows):
            for i in range(cols):
                cell_address = (i, j)  # col row
                cell_name = TableHelper.make_cell_name(col=i, row=j, zero_index=True)
                cell_obj = CellObj.from_idx(col_idx=i, row_idx=j, sheet_idx=sheet_idx)

                if cell_address > (0, 0):
                    # if this is the first cell in a row then the previous cell will be the last cell in the previous row
                    if i == 0:
                        prev_cell_address = (j - 1, cols - 1)
                    else:
                        prev_cell_address = (j, i - 1)
                    prev_cell_name = TableHelper.make_cell_name(
                        row=prev_cell_address[0], col=prev_cell_address[1], zero_index=True
                    )
                    mgr.add_source(f"{cell_name} = {prev_cell_name} + 1", cell=cell_obj)
                else:
                    # first cell
                    mgr.add_source(f"{cell_name} = 1", cell=cell_obj)

        count = 0
        for j in range(rows):
            for i in range(cols):
                count += 1
                cell_address = (i, j)  # col row
                cell = sheet[cell_address]
                assert cell.value == count

        fmn = tmp_path / "test_src_manager_across_down.ods"
        doc.save_doc(fmn)
        doc.close()

        doc = CalcDoc.open_doc(fnm=fmn, loader=loader)
        sheet = doc.sheets[0]
        # wipe out the values
        array = TableHelper.make_2d_array(rows, cols)
        sheet.set_array(values=array, name="A1")

        mgr = py_source_mgr.PySourceManager(doc)
        mgr.subscribe_after_source_update(cb=on_cell)
        # regenerate data
        mgr.update_all()

        count = 0
        for j in range(rows):
            for i in range(cols):
                count += 1
                cell_address = (i, j)  # col row
                cell_obj = CellObj.from_idx(col_idx=i, row_idx=j, sheet_idx=sheet_idx)
                cell = sheet[cell_obj]
                assert cell.value == count
    finally:
        if doc is not None:
            doc.close()


def test_src_manager_remove_cell_code(loader) -> None:
    if TYPE_CHECKING:
        from build.pythonpath.libre_pythonista_lib.code import py_source_mgr
        from build.pythonpath.libre_pythonista_lib.code import cell_cache
    else:
        from libre_pythonista_lib.code import py_source_mgr
        from libre_pythonista_lib.code import cell_cache

    def on_cell(src: Any, event_args: EventArgs) -> None:
        ed = cast(DotDict, event_args.event_data)
        if ed.result is not None:
            doc = cast(CalcDoc, ed.doc)
            sheet = doc.sheets[ed.sheet_idx]
            address = (ed.col, ed.row)
            sheet[address].value = ed.result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet["A1"]
        cell.value = 1
        cell_cache.CellCache.reset_instance(doc)
        mgr = py_source_mgr.PySourceManager(doc)
        mgr.subscribe_after_source_update(cb=on_cell)

        mgr.add_source("b1 = 0\na1 = 10", cell=cell.cell_obj)
        assert cell.value == 10
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 10

        cell = sheet["B1"]
        mgr.add_source("b1 = a1 + 10\nb1", cell=cell.cell_obj)
        assert cell.value == 20
        # b1 is now 20 if B1 cell is removed, then b1 var should go back to 0
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 20

        cell = sheet["A2"]
        mgr.add_source("a2 = b1 + 10", cell=cell.cell_obj)
        assert cell.value == 30
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 30

        cell = sheet["A3"]
        mgr.add_source("a3 = a2 + 10", cell=cell.cell_obj)
        assert cell.value == 40
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 40

        # remove b1
        cell = sheet["B1"]
        mgr.remove_source(cell=cell.cell_obj)

        cell = sheet["A1"]
        assert cell.value == 10
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 10

        # mgr.add_source("a2 = b1 + 10", cell=addr)
        # b1 is now 0 sor a2 should be 10
        cell = sheet["A2"]
        assert cell.value == 10
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 10

        cell = sheet["A3"]
        assert cell.value == 20
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 20

    finally:
        if doc is not None:
            doc.close()


def test_code_formula(loader) -> None:
    if TYPE_CHECKING:
        from build.pythonpath.libre_pythonista_lib.code import py_source_mgr
        from build.pythonpath.libre_pythonista_lib.code import cell_cache
    else:
        # import libre_pythonista_lib
        # import libre_pythonista
        from libre_pythonista_lib.code import py_source_mgr
        from libre_pythonista_lib.code import cell_cache

    def on_cell(src: Any, event_args: EventArgs) -> None:
        ed = cast(DotDict, event_args.event_data)
        if ed.result is not None:
            doc = cast(CalcDoc, ed.doc)
            sheet = doc.sheets[ed.sheet_idx]
            address = (ed.col, ed.row)
            sheet[address].value = ed.result

    def get_formula() -> str:
        return """def custom_formula(a, b):
    return a + b
"""

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet["A1"]
        cell.value = 1
        cell_cache.CellCache.reset_instance(doc)
        mgr = py_source_mgr.PySourceManager(doc)
        mgr.subscribe_after_source_update(cb=on_cell)
        mgr.add_source(get_formula(), cell=cell.cell_obj)

        cell = sheet["A2"]
        mgr.add_source("my_var = custom_formula(10, 12)", cell=cell.cell_obj)
        assert cell.value == 22
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 22

        cell = sheet["A3"]
        mgr.add_source("my_var2 = custom_formula(5, 5)", cell=cell.cell_obj)
        assert cell.value == 10
        py_src = mgr[cell.cell_obj]
        assert py_src.value == 10

    finally:
        if doc is not None:
            doc.close()
