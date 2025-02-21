from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_init_doc(loader, build_setup) -> None:
    """
    Tests initialization of a Calc document.

    Tests that a new Calc document can be created and initialized multiple times
    without error using CmdInitDoc.

    Args:
        loader: LibreOffice loader fixture
        build_setup: Test build setup fixture

    Raises:
        AssertionError: If initialization fails
    """
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import (
            QrySheetHasCalculationEvent,
        )
    else:
        from libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent

    doc = None
    try:
        # Create new Calc document
        doc = CalcDoc.create_doc(loader=loader)

        # Initialize document
        inst = CmdInitDoc(doc)
        inst.execute()
        assert inst.success

        # Test that document can be initialized multiple times
        inst.execute()
        assert inst.success

    finally:
        # Ensure document is closed even if test fails
        if not doc is None:
            doc.close(True)
