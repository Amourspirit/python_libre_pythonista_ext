from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_py_src_no_src(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.code.cmd_py_src import CmdPySrc
        from oxt.___lo_pip___.basic_config import BasicConfig as Config
    else:
        from libre_pythonista_lib.cmd.calc.code.cmd_py_src import CmdPySrc
        from libre_pythonista.basic_config import BasicConfig as Config

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        code = "x = 1\ny = 2\nz = x + y"
        cfg = Config()
        code_prop_name = cfg.cell_cp_codename
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        if not cell.has_custom_property(code_prop_name):
            cell.set_custom_property(code_prop_name, "code1_id")

        root_uri = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/{cfg.lp_code_dir}"
        code_id = cell.get_custom_property(code_prop_name)
        uri = f"{root_uri}/{sheet.unique_id}/{code_id}.py"

        cmd = CmdPySrc(code=code, uri=uri, cell=cell.cell_obj)
        cmd.execute()
        assert cmd.success

        assert cmd.py_src.exists()
        assert cmd.py_src.source_code == code

        cmd.undo()
        assert cmd.py_src.exists() is False
        assert cmd.py_src.source_code == ""
    finally:
        if not doc is None:
            doc.close(True)


def test_cmd_py_src_has_src(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.calc.code.cmd_py_src import CmdPySrc
        from oxt.___lo_pip___.basic_config import BasicConfig as Config
    else:
        from libre_pythonista_lib.cmd.calc.code.cmd_py_src import CmdPySrc
        from libre_pythonista.basic_config import BasicConfig as Config

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        code = "x = 1\ny = 2\nz = x + y"
        cfg = Config()
        code_prop_name = cfg.cell_cp_codename
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        if not cell.has_custom_property(code_prop_name):
            cell.set_custom_property(code_prop_name, "code1_id")

        root_uri = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/{cfg.lp_code_dir}"
        code_id = cell.get_custom_property(code_prop_name)
        uri = f"{root_uri}/{sheet.unique_id}/{code_id}.py"

        cmd = CmdPySrc(code=code, uri=uri, cell=cell.cell_obj)
        cmd.execute()
        assert cmd.success

        assert cmd.py_src.exists()
        assert cmd.py_src.source_code == code

        code2 = "a = 1\nb = 2\nc = a + b"

        cmd = CmdPySrc(code=code2, uri=uri, cell=cell.cell_obj)
        cmd.execute()
        assert cmd.success
        assert cmd.py_src.exists()
        assert cmd.py_src.source_code == code2

        cmd.undo()
        assert cmd.py_src.exists() is True
        assert cmd.py_src.source_code == code
    finally:
        if not doc is None:
            doc.close(True)
