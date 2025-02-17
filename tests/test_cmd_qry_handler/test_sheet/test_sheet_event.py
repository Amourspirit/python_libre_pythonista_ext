from __future__ import annotations

from typing import cast, TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_doc_event(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cache.mem_cache import MemCache
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache import QrySheetCache
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import (
            QrySheetCalculationEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import (
            QrySheetHasCalculationEvent,
        )
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_calc_formula import CmdSheetCalcFormula
        from oxt.___lo_pip___.basic_config import BasicConfig
    else:
        from libre_pythonista_lib.cache.mem_cache import MemCache
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache import QrySheetCache
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_calculation_event import QrySheetCalculationEvent
        from libre_pythonista_lib.query.calc.sheet.qry_sheet_has_calculation_event import QrySheetHasCalculationEvent
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
        qry_handler = QryHandler()
        cmd_handler = CmdHandler()

        qry_cache = QrySheetCache(sheet=sheet)
        cache = cast(MemCache, qry_handler.handle(qry_cache))

        has_calc_event = QrySheetHasCalculationEvent(sheet)
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False
        assert cache.hits == 0

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False
        assert cache.hits == 1
        last_hits = cache.hits

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""

        # check cached
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""
        assert cache.hits > last_hits
        last_hits = cache.hits

        cmd = CmdSheetCalcFormula(sheet)
        cmd_handler = CmdHandler()
        cmd_handler.handle(cmd)
        assert cmd.success

        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True
        assert cache.hits > last_hits
        last_hits = cache.hits

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result

        # check cached
        qry_result2 = qry_handler.handle(calc_event)
        assert qry_result == qry_result2
        assert cache.hits > last_hits
        last_hits = cache.hits

        doc.insert_sheet("Sheet 2")
        sheet = doc.sheets[1]

        qry_cache2 = QrySheetCache(sheet=sheet)
        cache2 = cast(MemCache, qry_handler.handle(qry_cache2))
        assert cache is not cache2

        has_calc_event = QrySheetHasCalculationEvent(sheet)
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False
        assert cache2.hits == 0
        last_hits = cache2.hits

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is False
        assert cache2.hits > last_hits
        last_hits = cache2.hits

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""

        # check cached
        qry_result = qry_handler.handle(calc_event)
        assert qry_result == ""
        assert cache2.hits > last_hits
        last_hits = cache2.hits

        cmd = CmdSheetCalcFormula(sheet)
        cmd_handler = CmdHandler()
        cmd_handler.handle(cmd)
        assert cmd.success

        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True

        # check cached
        qry_result = qry_handler.handle(has_calc_event)
        assert qry_result is True
        assert cache2.hits > last_hits
        last_hits = cache2.hits

        calc_event = QrySheetCalculationEvent(sheet)
        qry_result = qry_handler.handle(calc_event)
        assert qry_result

        # check cached
        qry_result2 = qry_handler.handle(calc_event)
        assert qry_result == qry_result2
        assert cache2.hits > last_hits
        last_hits = cache2.hits
    finally:
        if not doc is None:
            doc.close(True)
