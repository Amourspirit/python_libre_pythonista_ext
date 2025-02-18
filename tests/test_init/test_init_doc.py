from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_init_doc(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
    else:
        from libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        inst = CmdInitDoc(doc)
        inst.execute()
        assert inst.success
        inst.execute()
        assert inst.success
    finally:
        if not doc is None:
            doc.close(True)
