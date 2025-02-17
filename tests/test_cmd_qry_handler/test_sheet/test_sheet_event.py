from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_doc_event(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import (
            QrySheetCalculationEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import (
            QrySheetHasCalculationEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache import QryHandlerSheetCache
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache import CmdHandlerSheetCache
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
        from oxt.___lo_pip___.basic_config import BasicConfig
    else:
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import QrySheetCalculationEvent
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent
        from libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache import QryHandlerSheetCache
        from libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache import CmdHandlerSheetCache
        from libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
        from libre_pythonista.basic_config import BasicConfig

    doc = None
    try:
        # basic_config = BasicConfig()
        mock_config = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", BasicConfig)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: BasicConfig)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        qry_handler = QryHandlerSheetCache()
        cmd_handler = CmdHandlerSheetCache()
        has_calc_event = QrySheetHasCalculationEvent(sheet)
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""

        # check cached
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""

        cmd = CmdSheetCalcFormula(sheet)
        cmd_handler = CmdHandlerSheetCache()
        cmd_handler.handle(cmd)
        assert cmd.success

        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result

        # check cached
        qry_result2 = qry_handler.handle(calc_event)
        assert qry_result == qry_result2

        doc.insert_sheet("Sheet 2")
        sheet = doc.sheets[1]

        has_calc_event = QrySheetHasCalculationEvent(sheet)
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""

        # check cached
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""

        cmd = CmdSheetCalcFormula(sheet)
        cmd_handler = CmdHandlerSheetCache()
        cmd_handler.handle(cmd)
        assert cmd.success

        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result

        # check cached
        qry_result2 = qry_handler.handle(calc_event)
        assert qry_result == qry_result2
    finally:
        if not doc is None:
            doc.close(True)
