from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import ast
import types
import importlib.util
# import traceback

import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_doc_lru_cache(build_setup) -> None:
    if TYPE_CHECKING:
        from ...oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    else:
        from libre_pythonista_lib.doc.doc_globals import DocGlobals

    dg1 = DocGlobals(runtime_uid="1")
    dg2 = DocGlobals(runtime_uid="1")
    assert dg1 is dg2

    dg1.lru_cache["key"] = "value"
    assert dg2.lru_cache["key"] == "value"

    # delete singleton instance
    # delete_instance is a metaclass method
    DocGlobals.delete_instance(runtime_uid="1")
    dg = DocGlobals(runtime_uid="1")
    assert dg1 is not dg

    assert "key" not in dg.lru_cache

    dg.lru_cache["key"] = "value"
    assert dg.lru_cache["key"] == "value"

    dg4 = DocGlobals(runtime_uid="2")
    assert dg4 is not dg
    assert "key" not in dg4.lru_cache


def test_doc_from_lo(build_setup, loader) -> None:
    if TYPE_CHECKING:
        from ...oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    else:
        from libre_pythonista_lib.doc.doc_globals import DocGlobals

    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        uid = Lo.current_doc.runtime_uid

        doc_component = Lo.current_lo.desktop.get_current_component()
        uid = doc_component.RuntimeUID  # type: ignore

        dg1 = DocGlobals(runtime_uid=uid)
        dg2 = DocGlobals(runtime_uid=uid)
        assert dg1 is dg2
    finally:
        if doc is not None:
            doc.close(False)


def test_get_current(build_setup, loader) -> None:
    if TYPE_CHECKING:
        from ...oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    else:
        from libre_pythonista_lib.doc.doc_globals import DocGlobals

    from ooodev.calc import CalcDoc

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        dg1 = DocGlobals.get_current()
        dg2 = DocGlobals.get_current()
        assert dg1 is dg2

        dg1.lru_cache["key"] = "value"
        assert dg2.lru_cache["key"] == "value"
    finally:
        if doc is not None:
            doc.close(False)
