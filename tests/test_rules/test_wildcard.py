from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.wildcard import Wildcard


@pytest.mark.parametrize(
    "match",
    [
        ("==1.0.*"),
        ("==1.*"),
        ("==*"),
    ],
)
def test_is_match(match: str) -> None:
    rule = Wildcard(match)
    assert rule.get_is_match()


def test_get_version() -> None:
    ver = "==1.2.*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert versions[0].prefix == ">="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].micro == 0

    assert versions[1].prefix == "<"
    assert versions[1].major == 1
    assert versions[1].minor == 3
    assert versions[1].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=1.2, <1.3.0"

    ver = "==2.*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert versions[0].prefix == ">="
    assert versions[0].major == 2
    assert versions[0].minor == 0
    assert versions[0].micro == 0

    assert versions[1].prefix == "<"
    assert versions[1].major == 3
    assert versions[1].minor == 0
    assert versions[1].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=2, <3.0.0"

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
    ver = "==1.2.*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("1.2.9") == 0
    assert rule.get_version_is_valid("1.2.0") == 0
    assert rule.get_version_is_valid("1.1.0") == -1
    assert rule.get_version_is_valid("1.3") == 1

    ver = "==1.*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("1.2.9") == 0
    assert rule.get_version_is_valid("1.9.9") == 0
    assert rule.get_version_is_valid("0.2.9") == -1
    assert rule.get_version_is_valid("2.0.0") == 1

    ver = "==*"
    rule = Wildcard(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("0.0.1") == 0
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("0.0.1") == 0
    assert rule.get_version_is_valid("99.0.1") == 0


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "==1.2.*", True),
        ("1.2.5", "== 1.*", True),
        ("1.4.3", "==1.2.*", False),
        ("1.2.3", "==1.2.*", True),
        ("2.0.0", "==1.2.*", False),
        ("1.1.3", "==1.2.*", False),
        ("1.2.4", "==*", True),
    ],
)
def test_get_installed_valid(check_ver: str, vstr: str, result: bool) -> None:
    rule = Wildcard(vstr)
    assert rule.get_is_match()
    assert rule.get_installed_is_valid(check_ver) == result
