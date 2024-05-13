from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.lesser_equal import LesserEqual


@pytest.mark.parametrize(
    "match",
    [
        ("<=1.0.0"),
        ("<= 1.0"),
        ("<=  1"),
        ("<=0.0.1"),
        ("<=0.1.post1"),
        ("<= 0.1.dev1"),
        ("<=0.1.pre1"),
        ("<=0.1post1"),
        ("<=0.1dev1"),
        ("<= 0.1pre1"),
    ],
)
def test_is_match(match: str) -> None:
    rule = LesserEqual(match)
    assert rule.get_is_match()


def test_get_version() -> None:
    ver = "<=1.2.4"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == "<="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].micro == 4

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == "<=1.2.4"

    ver = "<=1.2.dev1"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == "<="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].dev == 1
    assert versions[0].is_devrelease

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == "<=1.2.dev1"

    ver = "<= 1.2pre1"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == "<="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].is_prerelease

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == "<=1.2rc1"

    ver = "<= 1.2pre1"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == "<="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].is_prerelease

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == "<=1.2rc1"

    ver = "<= 1.2.rc1"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == "<="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].is_prerelease

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == "<=1.2rc1"

    ver = "<= 1.2rc1"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 1
    assert versions[0].prefix == "<="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].is_prerelease

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == "<=1.2rc1"


def test_get_version_is_valid() -> None:
    ver = "<=1.2.4"
    rule = LesserEqual(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("1.2.5") == 1
    assert rule.get_version_is_valid("1.3.0") == 1
    assert rule.get_version_is_valid("2.0.0") == 1
    assert rule.get_version_is_valid("1.2.3") == 0
    assert rule.get_version_is_valid("0.0.3") == 0


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "<=1.2.4", 0),
        ("1.2.3", "<= 1.2.4", 0),
        ("1.2rc1", "<=1.2.pre1", 0),
        ("1.2rc1", "<=1.2.rc1", 0),
        ("1.2rc1", "<=1.2.pre2", 0),
        ("1.2rc2", "<=1.2.pre2", 0),
        ("1.2dev3", "<=1.2.dev3", 0),
        ("1.2dev1", "<=1.2dev2", 0),
        ("1.2dev3", "<=1.2dev2", 1),
        ("1.2post3", "<=1.2.post3", 0),
        ("1.2post1", "<=1.2post2", 0),
        ("1.2post3", "<=1.2post2", 1),
    ],
)
def test_get_version_is_valid_suffix(check_ver: str, vstr: str, result: int) -> None:
    rule = LesserEqual(vstr)
    assert rule.get_is_match()
    assert rule.get_version_is_valid(check_ver) == result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "<=1.2.4", True),
        ("1.2.3", "<= 1.2.4", True),
        ("1.2.5", "<= 1.2.4", True),
        ("1.2rc1", "<=1.2.pre1", True),
        ("1.2rc1", "<=1.2.rc1", True),
        ("1.2rc1", "<=1.2.pre2", True),
        ("1.2rc2", "<=1.2.pre2", True),
        ("1.2dev3", "<=1.2.dev3", True),
        ("1.2dev1", "<=1.2dev2", True),
        ("1.2dev3", "<=1.2dev2", True),
        ("1.2post3", "<=1.2.post3", True),
        ("1.2post1", "<=1.2post2", True),
        ("1.2post3", "<=1.2post2", True),
    ],
)
def test_get_installed_valid(check_ver: str, vstr: str, result: bool) -> None:
    rule = LesserEqual(vstr)
    assert rule.get_is_match()
    assert rule.get_installed_is_valid(check_ver) == result
