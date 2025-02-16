from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_provider(loader, build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.___lo_pip___.config import BasicConfig
        from oxt.pythonpath.libre_pythonista_lib.log.log_mixin_dummy import LogMixinDummy
        from oxt.pythonpath.libre_pythonista_lib.res.res_resolver_mixin_dummy import ResResolverMixinDummy
    else:
        from libre_pythonista.config import BasicConfig
        from libre_pythonista_lib.log.log_mixin_dummy import LogMixinDummy
        from libre_pythonista_lib.res.res_resolver_mixin_dummy import ResResolverMixinDummy

    # Create a mock logger
    mock_logger = mocker.Mock()

    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.mixin.ctl_namer_mixin.Config",
        BasicConfig,
    )
    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.mixin.ctl_namer_mixin.Config",
        new_callable=lambda: BasicConfig,
    )

    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider_default.Config",
        BasicConfig,
    )
    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider_default.Config",
        new_callable=lambda: BasicConfig,
    )

    # libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider_default

    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider_default.LogMixin",
        LogMixinDummy,
    )
    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.ctl_str.LogMixin",
        LogMixinDummy,
    )

    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.mixin.ctl_namer_mixin.LogMixin",
        LogMixinDummy,
    )

    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.ctl_str.ResResolverMixin",
        ResResolverMixinDummy,
    )
    _ = mocker.patch(
        "libre_pythonista_lib.pyc.cell.ctl.ctl_str.ResResolverMixin",
        new_callable=lambda: ResResolverMixinDummy,
    )

    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider_default import CtlProviderDefault
        from oxt.pythonpath.libre_pythonista_lib.pyc.cell.ctl.ctl_str import CtlStr
    else:
        from libre_pythonista_lib.pyc.cell.ctl.updater.ctl_provider_default import CtlProviderDefault
        from libre_pythonista_lib.pyc.cell.ctl.ctl_str import CtlStr

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        ctl = CtlStr(cell)

        mocker.patch.object(CtlProviderDefault, "log", new_callable=mocker.PropertyMock, return_value=mock_logger)
        provider = CtlProviderDefault(ctl)

        provider.add_ctl()
    finally:
        if doc is not None:
            doc.close()
