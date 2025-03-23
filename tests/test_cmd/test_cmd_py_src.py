from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_py_src_no_src(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
        from oxt.___lo_pip___.basic_config import BasicConfig as Config
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
        from libre_pythonista.basic_config import BasicConfig as Config
        from libre_pythonista_lib.utils.result import Result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        code = "x = 1\ny = 2\nz = x + y"
        cfg = Config()
        code_prop_name = cfg.cell_cp_codename
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        if not cell.has_custom_property(code_prop_name):
            cell.set_custom_property(code_prop_name, "code1_id")

        root_uri = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/{cfg.lp_code_dir}"
        code_id = cell.get_custom_property(code_prop_name)
        uri = f"{root_uri}/{sheet.unique_id}/{code_id}.py"

        qry_cell_uri = QryCellUri(cell=cell)
        qry_cell_uri_result = qry_handler.handle(qry_cell_uri)
        assert Result.is_success(qry_cell_uri_result)

        assert qry_cell_uri_result.data == uri

        cmd = CmdCellSrcCode(uri=uri, code=code, cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        py_src = PySource(uri=uri, cell=cell.cell_obj)
        assert py_src.exists()
        assert py_src.source_code == code

        cmd_handler.undo()
        assert py_src.exists() is False
        assert py_src.source_code == ""
    finally:
        if not doc is None:
            doc.close(True)


def test_cmd_py_src_has_src(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
        from oxt.___lo_pip___.basic_config import BasicConfig as Config
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.code.cmd_cell_src_code import CmdCellSrcCode
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
        from libre_pythonista.basic_config import BasicConfig as Config
        from libre_pythonista_lib.utils.result import Result

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        code = "x = 1\ny = 2\nz = x + y"
        cfg = Config()
        code_prop_name = cfg.cell_cp_codename
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        if not cell.has_custom_property(code_prop_name):
            cell.set_custom_property(code_prop_name, "code1_id")

        # root_uri = f"vnd.sun.star.tdoc:/{doc.runtime_uid}/{cfg.lp_code_dir}"
        # code_id = cell.get_custom_property(code_prop_name)
        # uri = f"{root_uri}/{sheet.unique_id}/{code_id}.py"

        uri = ""
        qry_cell_uri = QryCellUri(cell=cell)
        qry_result = qry_handler.handle(qry_cell_uri)

        assert Result.is_success(qry_result)
        uri = qry_result.data

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

        cmd_handler.undo()
        assert py_src.exists() is True
        assert py_src.source_code == code
    finally:
        if not doc is None:
            doc.close(True)
