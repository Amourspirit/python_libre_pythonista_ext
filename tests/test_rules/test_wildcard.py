from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.wildcard import Wildcard


@pytest.mark.parametrize(
    "match",
    [("==*")],
)
def test_is_match(match: str) -> None:
    rule = Wildcard(match)
    assert rule.get_is_match()


def test_get_version() -> None:
    ver = "==*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == ">="
    assert versions[0].major == 0
    assert versions[0].minor == 0
    assert versions[0].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=0.0.0"


def test_get_version_is_valid() -> None:
    ver = "==*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("0.0.1") == 0
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("0.0.1") == 0
    assert rule.get_version_is_valid("99.0.1") == 0


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [("1.2.4", "==*", True)],
)
def test_get_installed_valid(check_ver: str, vstr: str, result: bool) -> None:
    rule = Wildcard(vstr)
    assert rule.get_is_match()
    assert rule.get_installed_is_valid(check_ver) == result
