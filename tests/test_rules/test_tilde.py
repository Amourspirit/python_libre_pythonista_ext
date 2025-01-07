from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.tilde import Tilde


@pytest.mark.parametrize(
    "match",
    [
        ("~1.0.0"),
        ("~1.0"),
        ("~0.0.1"),
    ],
)
def test_is_match(match: str) -> None:
    rule = Tilde(match)
    assert rule.get_is_match()


@pytest.mark.parametrize(
    "match",
    [
        ("==1.0.0"),
        ("!=1.0"),
        ("~=1"),
        ("~=1.1"),
        ("~1.1a1"),
        ("*=0.0.1"),
    ],
)
def test_is_not_match(match: str) -> None:
    rule = Tilde(match)
    assert not rule.get_is_match()


def test_get_version() -> None:
    ver = "~1.2.3"
    rule = Tilde(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert versions[0].prefix == ">="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].micro == 3

    assert versions[1].prefix == "<"
    assert versions[1].major == 1
    assert versions[1].minor == 3
    assert versions[1].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=1.2.3, <1.3.0"

    ver = "~1.2"
    rule = Tilde(ver)
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
    assert pip_ver_str == ">=1.2.0, <1.3.0"

    ver = "~1.1"
    rule = Tilde(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert versions[0].prefix == ">="
    assert versions[0].major == 1
    assert versions[0].minor == 1
    assert versions[0].micro == 0

    assert versions[1].prefix == "<"
    assert versions[1].major == 1
    assert versions[1].minor == 2
    assert versions[1].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=1.1.0, <1.2.0"


@pytest.mark.parametrize(
    "ver,expect1,expect2",
    [
        pytest.param("~1.2.3", "1.2.3", "1.3.0", id="~1.2.3 low 1.2.3 hight 1.3.0"),
        pytest.param("~1.2", "1.2.0", "1.3.0", id="~1.2 low 1.2.0 hight 1.3.0"),
        pytest.param("~1", "1.0.0", "2.0.0", id="~1 low 1.0.0 hight 2.0.0"),
    ],
)
def test_get_version2(ver: str, expect1: str, expect2: str) -> None:
    # https://python-poetry.org/docs/dependency-specification/
    rule = Tilde(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert str(versions[0]) == expect1
    assert str(versions[1]) == expect2


def test_get_version_is_valid() -> None:
    ver = "~1.2.4"
    rule = Tilde(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("1.2.9") == 0
    assert rule.get_version_is_valid("1.2.3") == -1
    assert rule.get_version_is_valid("1.3") == 1


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "~1.2.4", 0),
        ("1.2.5", "~1.2.4", 0),
    ],
)
def test_get_version_is_valid_suffix(check_ver: str, vstr: str, result: int) -> None:
    rule = Tilde(vstr)
    assert rule.get_is_match()
    assert rule.get_version_is_valid(check_ver) == result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "~1.2.4", True),
        ("1.2.5", "~ 1.2.4", True),
        ("1.2.3", "~1.2.4", False),
    ],
)
def test_get_installed_valid(check_ver: str, vstr: str, result: bool) -> None:
    rule = Tilde(vstr)
    assert rule.get_is_match()
    assert rule.get_installed_is_valid(check_ver) == result
