from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_lp_version(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.___lo_pip___.basic_config import BasicConfig
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_lp_version import CmdLpVersion
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.ext.qry_ext_version import QryExtVersion
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_lp_version import QryLpVersion
        from oxt.pythonpath.libre_pythonista_lib.const import LP_EXT_VERSION
    else:
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.cmd.doc.cmd_lp_version import CmdLpVersion
        from libre_pythonista_lib.cq.qry.doc.ext.qry_ext_version import QryExtVersion
        from libre_pythonista_lib.cq.qry.doc.qry_lp_version import QryLpVersion
        from libre_pythonista_lib.const import LP_EXT_VERSION

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        config = BasicConfig()
        qry_handler = QryHandlerFactory.get_qry_handler()
        cmd_handler = CmdHandlerFactory.get_cmd_handler()

        qry_ext_ver = QryExtVersion()
        ext_ver = qry_handler.handle(qry_ext_ver)
        assert ext_ver == config.extension_version

        # Verify version is not set
        version_prop = doc.get_custom_property(LP_EXT_VERSION, None)
        assert version_prop is None

        qry_lp_ver = QryLpVersion(doc)
        lp_ver = qry_handler.handle(qry_lp_ver)
        assert lp_ver is None

        # Test initial state with no version
        cmd = CmdLpVersion(doc)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify version was set
        version_prop = doc.get_custom_property(LP_EXT_VERSION)
        assert version_prop == config.extension_version

        lp_ver = qry_handler.handle(qry_lp_ver)
        assert lp_ver == config.extension_version

        # Test executing when version is already set (should succeed but not change)
        cmd = CmdLpVersion(doc)
        cmd_handler.handle(cmd)
        assert cmd.success
        assert doc.get_custom_property(LP_EXT_VERSION) == config.extension_version

        # Test undo
        cmd_handler.handle_undo(cmd)
        assert doc.get_custom_property(LP_EXT_VERSION, None) == config.extension_version

        # Test error handling

        cmd = CmdLpVersion(doc)
        mocker.patch.object(cmd, "_get_current_state", side_effect=Exception("Test error"))

        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test undo when execute failed
        cmd_handler.handle_undo(cmd)  # should just log and return

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_lp_version_error_get_state(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_lp_version import CmdLpVersion
    else:
        from libre_pythonista_lib.cq.cmd.doc.cmd_lp_version import CmdLpVersion

    doc = mocker.MagicMock()

    cmd = CmdLpVersion(doc)
    mocker.patch.object(cmd, "_get_current_state", side_effect=Exception("Test error"))

    cmd.execute()
    assert not cmd.success
