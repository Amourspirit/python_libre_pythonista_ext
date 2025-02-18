from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_sheets_modified(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    else:
        from libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        cmd = CmdSheetsModified(doc)
        cmd.execute()
        assert cmd.success
    finally:
        if not doc is None:
            doc.close(True)


def test_cmd_sheets_modified_cell(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.events.args.event_args import EventArgs

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
        from oxt.pythonpath.libre_pythonista_lib.const.event_const import SHEET_MODIFIED
        from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    else:
        from libre_pythonista_lib.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
        from libre_pythonista_lib.const.event_const import SHEET_MODIFIED
        from libre_pythonista_lib.event.shared_event import SharedEvent

    doc = None
    try:
        fired = False

        def on(src: Any, event: EventArgs) -> None:  # noqa: ANN401
            nonlocal fired
            fired = True
            # event_args.event_data

        doc = CalcDoc.create_doc(loader=loader)
        se = SharedEvent()
        se.subscribe_event(SHEET_MODIFIED, on)

        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cell.value = "Hello"
        assert fired is False

        cmd = CmdSheetsModified(doc)
        cmd.execute()
        assert cmd.success
        cell.value = "nice"

        assert fired

        fired = False
        cmd.undo()
        cell.value = "World"
        assert fired is False

    finally:
        if not doc is None:
            doc.close(True)
