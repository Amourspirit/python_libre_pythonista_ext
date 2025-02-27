from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_qry_location(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.ext.qry_location import QryLocation
        from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from oxt.___lo_pip___.config import Config
    else:
        from libre_pythonista_lib.cq.query.doc.ext.qry_location import QryLocation
        from libre_pythonista_lib.cq.query.qry_handler import QryHandler
        from libre_pythonista.config import Config

    # Test shared installation
    mock_config = mocker.MagicMock(spec=Config)
    mock_config.is_shared_installed = True

    qry = QryLocation()
    mocker.patch.object(qry, "_get_config", return_value=mock_config)

    qry_handler = QryHandler()
    result = qry_handler.handle(qry)
    assert result == "share"

    # Test user installation
    mock_config.is_shared_installed = False
    result = qry_handler.handle(qry)
    assert result == "user"

    # Test exception handling
    mocker.patch.object(qry, "_get_config", side_effect=Exception("Test exception"))
    result = qry_handler.handle(qry)
    assert result == ""


def test_qry_location_kind(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.ext.qry_location import QryLocation
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    else:
        from libre_pythonista_lib.cq.query.doc.ext.qry_location import QryLocation
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    qry = QryLocation()
    assert qry.kind == CalcQryKind.SIMPLE

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
