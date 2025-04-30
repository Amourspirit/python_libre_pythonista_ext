from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_doc_event(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_doc_event import CmdDocEvent
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_doc_event import CmdDocEvent

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        cmd = CmdDocEvent(doc)
        cmd.execute()
        assert cmd.success
    finally:
        if not doc is None:
            doc.close(True)
