from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_handler_factory(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler_factory import CmdHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    else:
        from libre_pythonista_lib.cmd.cmd_handler_factory import CmdHandlerFactory
        from libre_pythonista_lib.cmd.cmd_handler import CmdHandler

    # Reset factory state
    CmdHandlerFactory.reset()

    # Test getting default handlers
    cmd_handler = CmdHandlerFactory.get_cmd_handler()

    assert isinstance(cmd_handler, CmdHandler)

    # Test setting custom handlers
    mock_cmd_handler = mocker.MagicMock()

    CmdHandlerFactory.set_cmd_handler(mock_cmd_handler)

    assert CmdHandlerFactory.get_cmd_handler() is mock_cmd_handler

    # Test reset
    CmdHandlerFactory.reset()

    assert CmdHandlerFactory.get_cmd_handler() is not mock_cmd_handler


def test_qry_handler_factory(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    else:
        from libre_pythonista_lib.query.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.query.qry_handler import QryHandler

    # Reset factory state
    QryHandlerFactory.reset()

    # Test getting default handlers
    qry_handler = QryHandlerFactory.get_qry_handler()

    assert isinstance(qry_handler, QryHandler)

    # Test setting custom handlers
    mock_qry_handler = mocker.MagicMock()

    QryHandlerFactory.set_qry_handler(mock_qry_handler)

    assert QryHandlerFactory.get_qry_handler() is mock_qry_handler

    # Test reset
    QryHandlerFactory.reset()

    assert QryHandlerFactory.get_qry_handler() is not mock_qry_handler
