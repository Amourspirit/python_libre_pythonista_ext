from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

from oxt.___lo_pip___.install.py_packages.py_package import PyPackage

# FILE: oxt/___lo_pip___/install/py_packages/test_py_package.py


@pytest.mark.parametrize(
    "ignore_platforms, platform, expected",
    [
        ({"win", "mac"}, "win", True),
        ({"win", "mac"}, "linux", False),
        ({"linux", "flatpak"}, "flatpak", True),
        ({"snap"}, "snap", True),
        ({"snap"}, "mac", False),
        (set(), "win", False),
    ],
)
def test_is_ignored_platform(ignore_platforms, platform, expected):
    package = PyPackage()
    package.ignore_platforms = ignore_platforms
    assert package.is_ignored_platform(platform) == expected
