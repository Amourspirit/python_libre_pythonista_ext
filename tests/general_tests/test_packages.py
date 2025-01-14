from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING

import pytest

if __name__ == "__main__":
    pytest.main([__file__])


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.parametrize(
    "is_flatpak,is_snap,os_name,py_version,num_pkg,packages",
    [
        pytest.param(
            False, False, "linux", "3.8.0", 1, [{"name": "requests", "version": "3.9.0"}], id="simple version"
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            0,
            [{"name": "requests", "version": "3.9.0", "python_versions": [">=3.9"]}],
            id="unmatched python version",
        ),
        pytest.param(
            False,
            False,
            "mac",
            "3.8.0",
            1,
            [
                {
                    "name": "verr",
                    "version": "1.2",
                    "restriction": ">=",
                    "python_versions": ["3.8"],
                    "platforms": ["all"],
                    "ignore_platforms": ["win"],
                }
            ],
            id="verr >=1.2 py3.8 all ignore win",
        ),
        pytest.param(
            False,
            False,
            "mac",
            "3.8.0",
            0,
            [
                {
                    "name": "verr",
                    "version": "1.2",
                    "restriction": ">=",
                    "python_versions": ["3.8"],
                    "platforms": ["all"],
                    "ignore_platforms": ["mac"],
                }
            ],
            id="verr mac ignore mac",
        ),
        pytest.param(
            False,
            False,
            "mac",
            "3.9.0",
            1,
            [
                {
                    "name": "spam1",
                    "version": "1.2",
                    "restriction": ">=",
                    "python_versions": ["==3.9"],
                }
            ],
            id="spam1 Python ==3.9",
        ),
        pytest.param(
            False,
            False,
            "mac",
            "3.9.0",
            0,
            [
                {
                    "name": "spam1",
                    "version": "1.2",
                    "restriction": ">=",
                    "python_versions": ["!=3.9"],
                }
            ],
            id="spam1 Python !=3.9",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.12.0",
            1,
            [{"name": "requests", "version": "3.9.0", "python_versions": ["3.12"]}],
            id="matched python version",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.12.0",
            0,
            [{"name": "requests", "version": "3.9.0", "python_versions": [">=3.9", "!=3.12"]}],
            id="Not equal python version 3.12",
        ),
        pytest.param(
            True,
            False,
            "linux",
            "3.8.0",
            0,
            [{"name": "requests", "version": "3.9.0", "ignore_platforms": ["mac", "flatpak"]}],
            id="ignore flatpak",
        ),
        pytest.param(
            True,
            False,
            "mac",
            "3.8.0",
            0,
            [{"name": "requests", "version": "3.9.0", "ignore_platforms": ["mac"]}],
            id="ignore mac",
        ),
        pytest.param(
            False,
            False,
            "win",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "platforms": ["win"]}],
            id="Window only",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "platforms": ["mac", "linux"]}],
            id="Mac and windows count = 1",
        ),
        pytest.param(
            False,
            False,
            "win",
            "3.12.0",
            0,
            [{"name": "requests", "version": "3.9.0", "platforms": ["mac", "linux"]}],
            id="Mac and windows count = 0",
        ),
        pytest.param(
            False,
            False,
            "win",
            "3.12.0",
            1,
            [{"name": "requests", "version": "3.9.0", "python_versions": ["3.12"]}],
            id="Python version 3.12 only",
        ),
    ],
)
def test_packages(
    is_flatpak: bool,
    is_snap: bool,
    os_name: str,
    py_version: str,
    num_pkg: int,
    packages: List[Dict[str, str]],
    mocker: MockerFixture,
) -> None:
    # package name and version are not being tested here.
    # python_versions is being tested here.
    # ignore_platforms is being tested here.
    def get_py_version() -> str:
        return py_version

    mock_config = mocker.patch("oxt.___lo_pip___.install.py_packages.packages.Config")
    mock_config_instance = mock_config.return_value
    mock_config_instance.is_flatpak = is_flatpak
    mock_config_instance.is_snap = is_snap
    if os_name == "win":
        mock_config_instance.is_win = True
    else:
        mock_config_instance.is_win = False

    if os_name == "mac":
        mock_config_instance.is_mac = True
    else:
        mock_config_instance.is_mac = False

    if os_name == "linux":
        mock_config_instance.is_linux = True
    else:
        mock_config_instance.is_linux = False

    _ = mocker.patch("oxt.___lo_pip___.install.py_packages.packages.OxtLogger")

    mock_pkg_config = mocker.patch("oxt.___lo_pip___.install.py_packages.packages.PackageConfig")
    mock_pkg_config_instance = mock_pkg_config.return_value
    py_packages = packages  # [{"name": "requests", "version": "3.9.0"}]
    # mocked_instance.py_packages.return_value = py_packages
    mock_pkg_config_instance.py_packages = py_packages

    if TYPE_CHECKING:
        from ...oxt.___lo_pip___.install.py_packages.packages import Packages
    else:
        from oxt.___lo_pip___.install.py_packages.packages import Packages

    mocker.patch.object(Packages, "_get_py_ver", side_effect=get_py_version)

    pkgs = Packages()
    assert len(pkgs.packages) == num_pkg


@pytest.mark.parametrize(
    "is_flatpak,is_snap,os_name,py_version,match_count,packages",
    [
        pytest.param(
            False, False, "linux", "3.8.0", 1, [{"name": "requests", "version": "3.9.0"}], id="simple version"
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            2,
            [{"name": "requests", "version": "3.9.0", "restriction": "^"}],
            id="Carrot restriction",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            2,
            [{"name": "requests", "version": "3", "restriction": "~"}],
            id="Tilde restriction",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            2,
            [{"name": "requests", "version": "3.1", "restriction": "~="}],
            id="Tilde Eq restriction",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "*", "restriction": "=="}],
            id="Wildcard restriction",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "restriction": "=="}],
            id="Equals version",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "restriction": ">="}],
            id="Greater Eq version",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "restriction": "<="}],
            id="LessThen Eq version",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "restriction": ">"}],
            id="Greater version",
        ),
        pytest.param(
            False,
            False,
            "linux",
            "3.8.0",
            1,
            [{"name": "requests", "version": "3.9.0", "restriction": "<"}],
            id="Less version",
        ),
    ],
)
def test_packages_rules(
    is_flatpak: bool,
    is_snap: bool,
    os_name: str,
    py_version: str,
    match_count: int,
    packages: List[Dict[str, str]],
    mocker: MockerFixture,
) -> None:
    # package name and version are not being tested here.
    # python_versions is being tested here.
    # ignore_platforms is being tested here.
    def get_py_version() -> str:
        return py_version

    mock_config = mocker.patch("oxt.___lo_pip___.install.py_packages.packages.Config")
    mock_config_instance = mock_config.return_value
    mock_config_instance.is_flatpak = is_flatpak
    mock_config_instance.is_snap = is_snap
    if os_name == "win":
        mock_config_instance.is_win = True
    else:
        mock_config_instance.is_win = False

    if os_name == "mac":
        mock_config_instance.is_mac = True
    else:
        mock_config_instance.is_mac = False

    if os_name == "linux":
        mock_config_instance.is_linux = True
    else:
        mock_config_instance.is_linux = False

    _ = mocker.patch("oxt.___lo_pip___.install.py_packages.packages.OxtLogger")

    mock_pkg_config = mocker.patch("oxt.___lo_pip___.install.py_packages.packages.PackageConfig")
    mock_pkg_config_instance = mock_pkg_config.return_value
    py_packages = packages  # [{"name": "requests", "version": "3.9.0"}]
    # mocked_instance.py_packages.return_value = py_packages
    mock_pkg_config_instance.py_packages = py_packages

    if TYPE_CHECKING:
        from ...oxt.___lo_pip___.install.py_packages.packages import Packages
        from ...oxt.___lo_pip___.ver.rules.ver_rules import VerRules
    else:
        from oxt.___lo_pip___.install.py_packages.packages import Packages
        from oxt.___lo_pip___.ver.rules.ver_rules import VerRules

    mocker.patch.object(Packages, "_get_py_ver", side_effect=get_py_version)

    pkgs = Packages()
    ver_rules = VerRules()
    for pkg in pkgs.packages:
        _, pkg_ver = pkg.name_version
        matched_rules = ver_rules.get_matched_rules(pkg_ver)
        assert len(matched_rules) == 1
        rule = matched_rules[0]
        versions = rule.get_versions()
        assert len(versions) == match_count
