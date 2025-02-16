from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_init_sheets(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.init_commands.cmd_init_sheets import CmdInitSheets
    else:
        from libre_pythonista_lib.cmd.calc.init_commands.cmd_init_sheets import CmdInitSheets

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        cmd = CmdInitSheets()
        cmd.execute()
        assert cmd.success
        cmd.execute()
        assert cmd.success
    finally:
        if not doc is None:
            doc.close(True)
