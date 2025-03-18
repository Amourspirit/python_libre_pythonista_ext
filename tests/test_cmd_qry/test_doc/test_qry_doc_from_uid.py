from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_qry_doc_from_uid(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_from_uid import QryDocFromUid
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.doc.qry_doc_from_uid import QryDocFromUid
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    doc = None
    try:
        # Create a test document
        doc = CalcDoc.create_doc(loader=loader)
        qry_handler = QryHandlerFactory.get_qry_handler()

        # Get the RuntimeUID of the created document
        uid = doc.runtime_uid

        # Create and execute query
        qry = QryDocFromUid(uid=uid)
        result = qry_handler.handle(qry)

        # Verify the query found the correct document
        assert result is not None
        assert result.runtime_uid == uid

        # Test with non-existent UID
        qry_invalid = QryDocFromUid(uid="non_existent_uid")
        result_invalid = qry_handler.handle(qry_invalid)
        assert result_invalid is None

    finally:
        if doc is not None:
            doc.close(True)


def test_qry_doc_from_uid_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_from_uid import QryDocFromUid
    else:
        from libre_pythonista_lib.cq.qry.doc.qry_doc_from_uid import QryDocFromUid

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        # Mock desktop.get_current_component to raise an exception
        mocker.patch(
            "ooodev.loader.Lo.current_lo.desktop.get_current_component", side_effect=Exception("Test exception")
        )

        qry = QryDocFromUid(uid=doc.runtime_uid)
        result = qry.execute()

        # Verify error handling returns None
        assert result is None

    finally:
        if doc is not None:
            doc.close(True)
