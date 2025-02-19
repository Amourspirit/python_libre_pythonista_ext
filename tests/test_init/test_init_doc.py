from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_init_doc(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import (
            QrySheetHasCalculationEvent,
        )
    else:
        from libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        inst = CmdInitDoc(doc)
        inst.execute()
        assert inst.success
        inst.execute()
        assert inst.success

        qry = QrySheetHasCalculationEvent(doc.sheets[0])
        handler = QryHandler()
        result = handler.handle(qry)
        assert result

    finally:
        if not doc is None:
            doc.close(True)
