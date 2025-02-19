from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_is_new_doc(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_is_doc_new import QryIsDocNew
    else:
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.query.calc.doc.qry_is_doc_new import QryIsDocNew

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        qry = QryIsDocNew(doc)
        handler = QryHandler()
        result = handler.handle(qry)
        assert result

    finally:
        if not doc is None:
            doc.close(True)


def test_is_existing_doc(loader, build_setup, copy_fix_calc) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.query.calc.doc.qry_is_doc_new import QryIsDocNew
    else:
        from libre_pythonista_lib.query.qry_handler import QryHandler
        from libre_pythonista_lib.query.calc.doc.qry_is_doc_new import QryIsDocNew

    doc = None
    try:
        file = copy_fix_calc("small_totals.ods")
        doc = CalcDoc.open_doc(fnm=file, loader=loader)

        qry = QryIsDocNew(doc)
        handler = QryHandler()
        result = handler.handle(qry)
        assert result is False

    finally:
        if not doc is None:
            doc.close(True)
