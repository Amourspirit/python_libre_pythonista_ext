from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple
from pathlib import Path
from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcSheet
from ooodev.loader.inst.options import Options
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
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
    else:
        # import libre_pythonista_lib
        # import libre_pythonista
        from libre_pythonista_lib.code import py_source_mgr

    def on_cell(src: Any, event_args: EventArgs) -> None:
        ed = cast(DotDict, event_args.event_data)
        if ed.result is not None:
            sheet = cast(CalcSheet, ed.sheet)
            address = (ed.col, ed.row)
            sheet[address].value = ed.result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet["A1"]
        cell.value = 1
        mgr = py_source_mgr.PySourceManager(sheet)
        mgr.subscribe_after_source_update(cb=on_cell)
        addr = (0, 0)  # A1
        mgr.add_source("print('Hello World!')\nx = 22", cell=addr)
        cell = sheet[addr]
        assert cell.value == 22

        addr = (0, 1)  # A2
        mgr.add_source("y = x + 10", cell=addr)
        cell = sheet[addr]
        assert cell.value == 32

        # A3
        addr = (0, 2)  # A3
        mgr.add_source("z = y + 10", cell=addr)
        cell = sheet[addr]
        assert cell.value == 42

        addr = (0, 3)  # A4
        mgr.add_source("aa = 'Nice!'", cell=addr)
        cell = sheet[addr]
        assert cell.value == "Nice!"

        addr = (0, 1)  # A2
        mgr.update_source("y = 223", cell=(0, 1))
        cell = sheet[addr]
        assert cell.value == 223

        # now that cell (0, 1), A2, is update to 223, A3 should be 233
        cell = sheet["A3"]
        assert cell.value == 233

        cell = sheet["A4"]
        assert cell.value == "Nice!"

    finally:
        if doc is not None:
            doc.close()


def test_src_manager_remove_cell_code(loader) -> None:

    if TYPE_CHECKING:
        from build.pythonpath.libre_pythonista_lib.code import py_source_mgr
    else:
        from libre_pythonista_lib.code import py_source_mgr

    def on_cell(src: Any, event_args: EventArgs) -> None:
        ed = cast(DotDict, event_args.event_data)
        if ed.result is not None:
            sheet = cast(CalcSheet, ed.sheet)
            address = (ed.col, ed.row)
            sheet[address].value = ed.result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet["A1"]
        cell.value = 1
        mgr = py_source_mgr.PySourceManager(sheet)
        mgr.subscribe_after_source_update(cb=on_cell)
        addr = (0, 0)  # A1
        mgr.add_source("b1 = 0\na1 = 10", cell=addr)
        cell = sheet[addr]
        assert cell.value == 10

        addr = (1, 0)  # B1
        mgr.add_source("b1 = a1 + 10\nb1", cell=addr)
        cell = sheet[addr]
        assert cell.value == 20
        # b1 is now 20 if B1 cell is removed, then b1 var should go back to 0

        addr = (0, 1)  # A2
        mgr.add_source("a2 = b1 + 10", cell=addr)
        cell = sheet[addr]
        assert cell.value == 30

        addr = (0, 2)  # A3
        mgr.add_source("a3 = a2 + 10", cell=addr)
        cell = sheet[addr]
        assert cell.value == 40

        # remove b1
        mgr.remove_source(cell=(1, 0))

        addr = (0, 0)  # A1
        cell = sheet[addr]
        assert cell.value == 10

        # mgr.add_source("a2 = b1 + 10", cell=addr)
        # b1 is now 0 sor a2 should be 10
        addr = (0, 1)  # A2
        cell = sheet[addr]
        assert cell.value == 10

        addr = (0, 2)  # A3
        cell = sheet[addr]
        assert cell.value == 20

    finally:
        if doc is not None:
            doc.close()
