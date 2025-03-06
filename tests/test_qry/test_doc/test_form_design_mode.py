from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture
from ooodev.calc import CalcDoc
from ooodev.exceptions import ex as mEx

if __name__ == "__main__":
    pytest.main([__file__])


def test_form_design_mode(loader, build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_form_design_mode import QryFormDesignMode
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
    else:
        from libre_pythonista_lib.cq.qry.calc.doc.qry_form_design_mode import QryFormDesignMode
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        qry = QryFormDesignMode(doc)
        qry_handler = QryHandler()

        # Test normal case - is in design mode
        result = qry_handler.handle(qry)
        assert result is True

        # Mock view to return True for form design mode
        mock_view = mocker.MagicMock()
        mock_view.view_controller_name = "Default"
        mock_view.is_form_design_mode.return_value = True
        mocker.patch.object(doc, "get_view", return_value=mock_view)

        result = qry_handler.handle(qry)
        assert result is True

        # Test different view controller (e.g. print preview)
        mock_view.view_controller_name = "PrintPreview"
        result = qry_handler.handle(qry)
        assert result is None

        # Test MissingInterfaceError
        mocker.patch.object(doc, "get_view", side_effect=mEx.MissingInterfaceError("Test error"))
        result = qry_handler.handle(qry)
        assert result is None

        # Test general exception in is_form_design_mode
        mock_view = mocker.MagicMock()
        mock_view.view_controller_name = "Default"
        mock_view.is_form_design_mode.side_effect = Exception("Test error")
        mocker.patch.object(doc, "get_view", return_value=mock_view)

        result = qry_handler.handle(qry)
        assert result is None

    finally:
        if doc is not None:
            doc.close(True)


def test_form_design_mode_kind(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_form_design_mode import QryFormDesignMode
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    else:
        from libre_pythonista_lib.cq.qry.calc.doc.qry_form_design_mode import QryFormDesignMode
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        qry = QryFormDesignMode(doc)

        # Test default kind
        assert qry.kind == CalcQryKind.SIMPLE

        # Test setting kind
        qry.kind = CalcQryKind.SHEET_CACHE
        assert qry.kind == CalcQryKind.SHEET_CACHE

    finally:
        if doc is not None:
            doc.close(True)
