from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_url_info(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import UrlInfo
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import UrlInfo
    root_url = "vnd.sun.star.tdoc:/1/random_dir"
    sheet_unique_id = "rr34jlkj53"
    code_id = "reu44340ttr"
    uri = f"{root_url}/{sheet_unique_id}/{code_id}.py"
    info = UrlInfo.from_url(uri)
    assert info.url == uri
    assert info.full_name == f"{code_id}.py"
    assert info.protocol == "vnd.sun.star.tdoc:"
    assert info.path == f"1/random_dir/{sheet_unique_id}/{code_id}.py"
    assert info.runtime_id == "1"
    assert info.code_dir == "random_dir"
    assert info.unique_id == sheet_unique_id
    assert info.name == code_id
    assert info.ext == "py"


def test_py_src(build_setup, loader) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import UrlInfo
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import UrlInfo
    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        co = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
        src_code = "print('Hello')"
        root_url = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/random_dir"
        sheet_unique_id = "rr34jlkj53"
        code_id = "reu44340ttr"
        uri = f"{root_url}/{sheet_unique_id}/{code_id}.py"
        info = UrlInfo.from_url(uri)
        py_src = PySource(uri=info.url, cell=co)
        assert py_src.exists() is False
        py_src.source_code = src_code
        assert py_src.exists()
        assert py_src.source_code == src_code
        assert py_src.col == 0
        assert py_src.row == 0
        assert py_src.sheet_idx == 0
        assert py_src.uri_info.unique_id == sheet_unique_id

        src_code = "print('World')"
        py_src.source_code = src_code
        assert py_src.source_code == src_code
    finally:
        if not doc is None:
            doc.close()
