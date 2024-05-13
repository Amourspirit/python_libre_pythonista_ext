from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.tilde import Tilde


@pytest.mark.parametrize(
    "match",
    [
        ("~=1.0.0"),
        ("~=1.0"),
        ("~=0.0.1"),
        ("~=0.1.post1"),
        ("~=0.1.dev1"),
        ("~=0.1.pre1"),
        ("~=0.1post1"),
        ("~=0.1dev1"),
        ("~=0.1pre1"),
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
        ("*=0.0.1"),
    ],
)
def test_is_not_match(match: str) -> None:
    rule = Tilde(match)
    assert rule.get_is_match() == False


def test_get_version() -> None:
    ver = "~=1.2.3"
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

    ver = "~=1.2"
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
    assert pip_ver_str == ">=1.2, <1.3.0"

    ver = "~=1.1"
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
    assert pip_ver_str == ">=1.1, <1.2.0"


def test_get_version_is_valid() -> None:
    ver = "~=1.2.4"
    rule = Tilde(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("1.2.9") == 0
    assert rule.get_version_is_valid("1.2.3") == -1
    assert rule.get_version_is_valid("1.3") == 1


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "~=1.2.4", 0),
        ("1.2.5", "~= 1.2.4", 0),
        ("1.2rc1", "~=1.2.pre1", 0),
        ("1.2rc1", "~=1.2.rc1", 0),
        ("1.2rc1", "~=1.2.pre2", -1),
        ("1.2rc2", "~=1.2.pre2", 0),
        ("1.2dev3", "~=1.2.dev3", 0),
        ("1.2dev1", "~=1.2dev2", -1),
        ("1.3dev3", "~=1.2dev2", 0),  # 1.3dev3 is less than 1.3.0 becuase it is a dev version
        ("1.2post3", "~=1.2.post3", 0),
        ("1.2post1", "~=1.2post2", -1),
        ("1.2post3", "~=1.2post2", 0),
        ("2.2", "~=1.2post2", 1),
    ],
)
def test_get_version_is_valid_suffix(check_ver: str, vstr: str, result: int) -> None:
    rule = Tilde(vstr)
    assert rule.get_is_match()
    assert rule.get_version_is_valid(check_ver) == result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "~=1.2.4", True),
        ("1.2.5", "~= 1.2.4", True),
        ("1.2.3", "~= 1.2.4", False),
        ("1.2rc1", "~=1.2.pre1", True),
        ("1.2rc1", "~=1.2.rc1", True),
        ("1.2rc1", "~=1.2.pre2", False),
        ("1.2rc2", "~=1.2.pre2", True),
        ("1.2dev3", "~=1.2.dev3", True),
        ("1.2dev1", "~=1.2dev2", False),
        ("1.3dev3", "~=1.2dev2", True),  # 1.3dev3 is less than 1.3.0 becuase it is a dev version
        ("1.2post3", "~=1.2.post3", True),
        ("1.2post1", "~=1.2post2", False),
        ("1.2post3", "~=1.2post2", True),
        ("2.2", "~=1.2post2", False),
    ],
)
def test_get_installed_valid(check_ver: str, vstr: str, result: bool) -> None:
    rule = Tilde(vstr)
    assert rule.get_is_match()
    assert rule.get_installed_is_valid(check_ver) == result
