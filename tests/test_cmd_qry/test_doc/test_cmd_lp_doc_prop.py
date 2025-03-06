from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_lp_doc_prop(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_prop import QryLpDocProp
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_prop import CmdLpDocProp
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
        from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
        from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_prop import QryLpDocProp
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_prop import CmdLpDocProp

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        test_props = {"test_key": "test_value"}
        cmd = CmdLpDocProps(doc=doc, props=test_props)
        qry_handler = QryHandlerFactory.get_qry_handler()
        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        # not cached ver
        cmd_handler.handle(cmd)

        # none cached ver
        qry = QryLpDocProps(doc)
        result = qry_handler.handle(qry)
        assert result is not None
        assert result == test_props

        # cached ver
        qry = QryLpDocProps(doc)
        result = qry_handler.handle(qry)
        assert result is not None
        assert result == test_props

        qry_prop = QryLpDocProp(doc, "test_key")
        result = qry_handler.handle(qry_prop)
        assert result == "test_value"

        cmd_prop = CmdLpDocProp(doc, "test_key", "new_value")
        cmd_handler.handle(cmd_prop)

        result = qry_handler.handle(qry_prop)
        assert result == "new_value"

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_lp_doc_props_cache_keys(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
        from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA
    else:
        from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
        from libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA

    doc = mocker.Mock()
    cmd = CmdLpDocProps(doc=doc, props={})
    assert cmd.cache_keys == (DOC_LP_DOC_PROP_DATA,)


def test_qry_lp_doc_props_cache_keys(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
        from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA
    else:
        from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
        from libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA

    doc = mocker.Mock()
    cmd = QryLpDocProps(doc=doc)
    assert cmd.cache_key == DOC_LP_DOC_PROP_DATA
