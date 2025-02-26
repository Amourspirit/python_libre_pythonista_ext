from __future__ import annotations

from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_new_doc(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
    else:
        from libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from libre_pythonista_lib.cq.query.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        qry = QryIsDocPythonista(doc)
        handler = QryHandler()
        result = handler.handle(qry)
        assert result is False

    finally:
        if not doc is None:
            doc.close(True)


def test_existing_doc(loader, build_setup, copy_fix_calc) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
    else:
        from libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from libre_pythonista_lib.cq.query.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista

    doc = None
    try:
        file = copy_fix_calc("small_totals.ods")
        doc = CalcDoc.open_doc(fnm=file, loader=loader)

        qry = QryIsDocPythonista(doc)
        handler = QryHandler()
        result = handler.handle(qry)
        assert result is False

    finally:
        if not doc is None:
            doc.close(True)


def test_existing_lp_doc(loader, build_setup, copy_fix_calc) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista
    else:
        from libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from libre_pythonista_lib.cq.query.calc.doc.qry_is_doc_pythonista import QryIsDocPythonista

    doc = None
    try:
        file = copy_fix_calc("lp_simple.ods")
        doc = CalcDoc.open_doc(fnm=file, loader=loader)

        qry = QryIsDocPythonista(doc)
        handler = QryHandler()
        result = handler.handle(qry)
        assert result

    finally:
        if not doc is None:
            doc.close(True)
