from __future__ import annotations
from typing import TYPE_CHECKING, cast
import pytest
from pytest_mock import MockerFixture
from ooodev.utils.gen_util import NULL_OBJ

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_calc_props(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_calc_props import CmdCalcProps
        from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_calc_props import QryCalcProps
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.___lo_pip___.config import Config
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_calc_props import CmdCalcProps
        from libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from libre_pythonista_lib.cq.qry.calc.doc.qry_calc_props import QryCalcProps
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista.config import Config

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        log_fmt = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"

        mock_config = mocker.MagicMock(spec=Config)
        mock_config.is_shared_installed = True
        mock_config.lp_default_log_format = log_fmt

        # Patch the Config class in calc_props2 module
        mocker.patch("libre_pythonista_lib.doc_props.calc_props2.Config", return_value=mock_config)

        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()

        # Create initial properties
        qry = QryCalcProps(doc)
        initial_props = qry_handler.handle(qry)
        # changing initial_props properties here also changes in the cache
        # because it is a reference to the same object
        assert initial_props.log_to_console is False
        assert initial_props.log_format == log_fmt

        # Create command
        cmd = CmdCalcProps(doc=doc, props=initial_props)

        initial_props.log_to_console = True
        # Test initial state
        assert cmd.kind == CalcCmdKind.SIMPLE_CACHE
        assert cmd.cache_keys == (DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA)
        assert not cmd.success

        # Execute command
        cmd_handler.handle(cmd)
        assert cmd.success

        new_props = qry_handler.handle(qry)
        assert new_props.log_to_console is True

        # Test undo
        cmd_handler.handle_undo(cmd)
        original_props = qry_handler.handle(qry)
        assert original_props.log_to_console is False

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_calc_props_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_calc_props import CmdCalcProps
        from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from oxt.___lo_pip___.config import Config
    else:
        from libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_calc_props import CmdCalcProps
        from libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
        from libre_pythonista.config import Config

    doc = mocker.Mock()

    log_fmt = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
    mock_config = mocker.MagicMock(spec=Config)
    mock_config.is_shared_installed = True
    mock_config.lp_default_log_format = log_fmt

    # Patch the Config class in calc_props2 module
    mocker.patch("libre_pythonista_lib.doc_props.calc_props2.Config", return_value=mock_config)

    props = CalcProps2()

    cmd = CmdCalcProps(doc=doc, props=props)
    assert cmd.kind == CalcCmdKind.SIMPLE_CACHE
    assert cmd.cache_keys == (DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA)

    cmd.kind = CalcCmdKind.CELL
    assert cmd.kind == CalcCmdKind.CELL
