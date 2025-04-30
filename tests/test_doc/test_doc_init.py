from __future__ import annotations
from typing import TYPE_CHECKING

import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_doc_init(build_setup, loader) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.doc_init import DocInit
    else:
        from libre_pythonista_lib.doc.doc_init import DocInit

    from ooodev.calc import CalcDoc

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        doc_init = DocInit(doc)
        assert doc_init.is_doc_init() is False
        doc_init.ensure_doc_init()
        assert doc_init.is_doc_init() is True
        doc_init.ensure_doc_init()
        assert doc_init.is_doc_init() is True
        doc_init2 = DocInit(doc)
        assert doc_init2 is doc_init

    finally:
        if doc is not None:
            doc.close(False)
