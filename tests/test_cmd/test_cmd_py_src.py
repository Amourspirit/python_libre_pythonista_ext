from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_py_src_no_src(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySource
        from oxt.___lo_pip___.basic_config import BasicConfig as Config
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.pyc.code.py_source import PySource
        from libre_pythonista.basic_config import BasicConfig as Config

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        code = "x = 1\ny = 2\nz = x + y"
        cfg = Config()
        code_prop_name = cfg.cell_cp_codename
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()

        if not cell.has_custom_property(code_prop_name):
            cell.set_custom_property(code_prop_name, "code1_id")

        root_uri = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/{cfg.lp_code_dir}"
        code_id = cell.get_custom_property(code_prop_name)
        uri = f"{root_uri}/{sheet.unique_id}/{code_id}.py"

        cmd = CmdCellSrcCode(code=code, uri=uri, cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        py_src = PySource(uri=uri, cell=cell.cell_obj)
        assert py_src.exists()
        assert py_src.source_code == code

        cmd.undo()
        assert py_src.exists() is False
        assert py_src.source_code == ""
    finally:
        if not doc is None:
            doc.close(True)


def test_cmd_py_src_has_src(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySource
        from oxt.___lo_pip___.basic_config import BasicConfig as Config
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.pyc.code.py_source import PySource
        from libre_pythonista.basic_config import BasicConfig as Config

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        code = "x = 1\ny = 2\nz = x + y"
        cfg = Config()
        code_prop_name = cfg.cell_cp_codename
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()

        if not cell.has_custom_property(code_prop_name):
            cell.set_custom_property(code_prop_name, "code1_id")

        root_uri = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/{cfg.lp_code_dir}"
        code_id = cell.get_custom_property(code_prop_name)
        uri = f"{root_uri}/{sheet.unique_id}/{code_id}.py"

        cmd = CmdCellSrcCode(code=code, uri=uri, cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success

        py_src = PySource(uri=uri, cell=cell.cell_obj)

        assert py_src.exists()
        assert py_src.source_code == code

        code2 = "a = 1\nb = 2\nc = a + b"

        cmd = CmdCellSrcCode(code=code2, uri=uri, cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert py_src.exists()
        assert py_src.source_code == code2

        cmd.undo()
        assert py_src.exists() is True
        assert py_src.source_code == code
    finally:
        if not doc is None:
            doc.close(True)
