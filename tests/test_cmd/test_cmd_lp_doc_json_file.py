from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_lp_doc_json_file(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file_del import CmdLpDocJsonFileDel
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from oxt.___lo_pip___.basic_config import BasicConfig
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
        from libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file_del import CmdLpDocJsonFileDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.query.qry_handler_factory import QryHandlerFactory
        from libre_pythonista.basic_config import BasicConfig

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        cmd = CmdLpDocJsonFile(doc)

        # Test kind property
        assert cmd.kind == CalcCmdKind.SIMPLE_CACHE

        # Test file_name construction
        cfg = BasicConfig()
        expected_file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"

        # Test cache_keys property
        assert len(cmd.cache_keys) == 1
        assert cmd.cache_keys[0] == f"DocJsonFile_{expected_file_name}"

        assert cmd.file_name == expected_file_name

        qry_handler = QryHandlerFactory.get_qry_handler()
        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        qry = QryLpDocJsonFile(doc)

        # not cached ver
        result = qry_handler.handle(qry)
        assert result is None

        cmd_handler.handle(cmd)
        assert cmd.success

        # not cached ver
        result = qry_handler.handle(qry)
        assert result is not None

        # cached ver
        result = qry_handler.handle(qry)
        assert result is not None

        cmd_del = CmdLpDocJsonFileDel(doc)
        cmd_handler.handle(cmd_del)
        assert cmd_del.success

        result = qry_handler.handle(qry)
        assert result is None

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_lp_doc_json_file_mock(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    mock_doc = mocker.MagicMock()
    cmd = CmdLpDocJsonFile(doc=mock_doc)

    # Test kind property
    assert cmd.kind == CalcCmdKind.SIMPLE_CACHE

    # Test that kind can be set
    cmd.kind = CalcCmdKind.SIMPLE
    assert cmd.kind == CalcCmdKind.SIMPLE
