from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_create_read_control(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import create_control
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import get_control
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import create_control
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import get_control
        from libre_pythonista_lib.kind.ctl_kind import CtlKind

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        created_ctl = create_control(cell, CtlKind.STRING)
        assert created_ctl is not None
        assert created_ctl.calc_cell == cell

        read_ctl = get_control(cell)
        assert read_ctl is not None
        assert read_ctl.calc_cell == cell

    finally:
        if doc is not None:
            doc.close(True)
