from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_sheet_ensure_forms(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_ensure_forms import CmdSheetEnsureForms
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.qry_form_name import QryFormName
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_ensure_forms import CmdSheetEnsureForms
        from libre_pythonista_lib.cq.qry.calc.common.qry_form_name import QryFormName
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]

        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        # Get form name that will be used
        qry = QryFormName()
        form_name = qry_handler.handle(qry)

        # Initial state - no forms should exist
        assert len(sheet.draw_page.forms) == 0
        assert not sheet.draw_page.forms.has_by_name("Form1")
        assert not sheet.draw_page.forms.has_by_name(form_name)

        # Execute command
        cmd = CmdSheetEnsureForms(sheet)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify forms were created
        assert len(sheet.draw_page.forms) == 2
        assert sheet.draw_page.forms.has_by_name("Form1")
        assert sheet.draw_page.forms.has_by_name(form_name)

        # Test executing again (should do nothing)
        cmd = CmdSheetEnsureForms(sheet)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert len(sheet.draw_page.forms) == 2

        # Test undo
        cmd_handler.undo()
        assert len(sheet.draw_page.forms) == 2  # undo does nothing if forms existed initially

        # Test creating and then undoing when no forms existed initially
        sheet.draw_page.forms.remove_by_name("Form1")
        sheet.draw_page.forms.remove_by_name(form_name)
        assert len(sheet.draw_page.forms) == 0

        cmd = CmdSheetEnsureForms(sheet)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert len(sheet.draw_page.forms) == 2

        cmd_handler.undo()
        assert len(sheet.draw_page.forms) == 0

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_sheet_ensure_forms_failure(loader, build_setup, mocker) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_ensure_forms import CmdSheetEnsureForms
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_ensure_forms import CmdSheetEnsureForms

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]

        # Test failure during execution
        cmd = CmdSheetEnsureForms(sheet)
        mocker.patch.object(sheet.draw_page.forms, "add_form", side_effect=Exception("Simulated error"))

        cmd.execute()
        assert not cmd.success
        assert len(sheet.draw_page.forms) == 0

        # Test undo when not successful
        cmd.undo()  # should just log "Undo not needed"
        assert len(sheet.draw_page.forms) == 0

    finally:
        if doc is not None:
            doc.close(True)
