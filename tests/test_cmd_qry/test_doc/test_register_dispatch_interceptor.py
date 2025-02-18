from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_register(loader, py_src_uri, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.cmd_register_dispatch_interceptor import (
            CmdRegisterDispatchInterceptor,
        )
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.cmd_unregister_dispatch_interceptor import (
            CmdUnRegisterDispatchInterceptor,
        )
        from oxt.pythonpath.libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import (
            CalcSheetCellDispatchProvider,
        )
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from oxt.___lo_pip___.basic_config import BasicConfig

    else:
        from libre_pythonista_lib.cmd.calc.doc.cmd_register_dispatch_interceptor import CmdRegisterDispatchInterceptor
        from libre_pythonista_lib.cmd.calc.doc.cmd_unregister_dispatch_interceptor import (
            CmdUnRegisterDispatchInterceptor,
        )
        from libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider import CalcSheetCellDispatchProvider
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
        from libre_pythonista.basic_config import BasicConfig

    doc = None
    try:
        mock_lp_settings = mocker.Mock()
        mock_lp_settings_inst = mock_lp_settings.return_value
        mock_lp_settings_inst.experimental_editor = False

        mock_config = mocker.patch(
            "libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider.Config", BasicConfig
        )
        _ = mocker.patch(
            "libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider.Config", new_callable=lambda: BasicConfig
        )
        mocker.patch.object(mock_config, "lp_settings", mock_lp_settings_inst, create=True)
        doc = CalcDoc.create_doc(loader=loader)
        cmd_handler = CmdHandler()
        assert CalcSheetCellDispatchProvider.has_instance(doc) == False
        cmd = CmdRegisterDispatchInterceptor(doc)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert CalcSheetCellDispatchProvider.has_instance(doc) == True

        cmd = CmdUnRegisterDispatchInterceptor(doc)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert CalcSheetCellDispatchProvider.has_instance(doc) == False

    finally:
        if not doc is None:
            doc.close(True)
