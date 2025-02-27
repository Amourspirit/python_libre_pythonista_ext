from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_doc_lp_props(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_lp_props import CmdDocLpProps
        from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_doc_lp_props import QryDocLpProps
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_PROPERTIES
        from oxt.___lo_pip___.basic_config import BasicConfig
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_lp_props import CmdDocLpProps
        from libre_pythonista_lib.cq.query.calc.doc.qry_doc_lp_props import QryDocLpProps
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.query.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.const.cache_const import DOC_LP_PROPERTIES
        from libre_pythonista.basic_config import BasicConfig

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        cmd = CmdDocLpProps(doc)

        # Test kind property
        assert cmd.kind == CalcCmdKind.SIMPLE_CACHE

        # Test cache_keys property
        assert len(cmd.cache_keys) == 1
        assert cmd.cache_keys[0] == DOC_LP_PROPERTIES

        # Test file_name construction
        cfg = BasicConfig()
        expected_file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"
        assert cmd._file_name == expected_file_name

        qry_handler = QryHandlerFactory.get_qry_handler()
        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        qry = QryDocLpProps(doc)

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

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_doc_lp_props_mock(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_lp_props import CmdDocLpProps
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_lp_props import CmdDocLpProps
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    mock_doc = mocker.MagicMock()
    cmd = CmdDocLpProps(doc=mock_doc)

    # Test kind property
    assert cmd.kind == CalcCmdKind.SIMPLE_CACHE

    # Test that kind can be set
    cmd.kind = CalcCmdKind.SIMPLE
    assert cmd.kind == CalcCmdKind.SIMPLE
