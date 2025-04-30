from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_init_doc(loader, build_setup, mocker: MockerFixture) -> None:
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
        from oxt.___lo_pip___.basic_config import BasicConfig

    else:
        from libre_pythonista.basic_config import BasicConfig

    mock_lp_settings = mocker.Mock()
    mock_lp_settings_inst = mock_lp_settings.return_value
    mock_lp_settings_inst.experimental_editor = False

    mock_config = mocker.patch("libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider.Config", BasicConfig)
    _ = mocker.patch(
        "libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider.Config", new_callable=lambda: BasicConfig
    )
    mocker.patch.object(mock_config, "lp_settings", mock_lp_settings_inst, create=True)

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
    else:
        from libre_pythonista_lib.cq.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc

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
