from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_sheets_activation(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import (
            CmdSheetActivation,
        )
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        cmd = CmdSheetActivation(doc)
        cmd.execute()
        assert cmd.success
    finally:
        if not doc is None:
            doc.close(True)


def test_cmd_sheets_activation_sheet_insert(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.events.args.event_args import EventArgs

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import (
            CmdSheetActivation,
        )
        from oxt.pythonpath.libre_pythonista_lib.const.event_const import SHEET_ACTIVATION
        from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
        from libre_pythonista_lib.const.event_const import SHEET_ACTIVATION
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

    doc = None
    try:
        fired = False

        def on(src: Any, event: EventArgs) -> None:  # noqa: ANN401
            nonlocal fired
            fired = True
            # event_args.event_data

        doc = CalcDoc.create_doc(loader=loader)
        se = SharedEvent()
        se.subscribe_event(SHEET_ACTIVATION, on)
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        cmd = CmdSheetActivation(doc)
        cmd_handler.handle(cmd)
        assert cmd.success

        doc.sheets.insert_sheet("Sheet 2")
        doc.sheets.set_active_sheet(doc.sheets[1])

        assert fired

        fired = False

        cmd_handler.handle_undo(cmd)
        assert cmd._listener is cmd._undo_listener  # test singleton
        doc.sheets.set_active_sheet(doc.sheets[0])
        assert fired is False

    finally:
        if not doc is None:
            doc.close(True)
