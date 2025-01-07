from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.carrot import Carrot


@pytest.mark.parametrize(
    "match",
    [
        ("^1.0.0"),
        ("^1.0"),
        ("^1"),
        ("^0.0.1"),
    ],
)
def test_is_match(match: str) -> None:
    rule = Carrot(match)
    assert rule.get_is_match()


def test_get_version() -> None:
    ver = "^1.2.4"
    rule = Carrot(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert versions[0].prefix == ">="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].micro == 4

    assert versions[1].prefix == "<"
    assert versions[1].major == 2
    assert versions[1].minor == 0
    assert versions[1].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=1.2.4, <2.0.0"

    ver = "^1.2.dev1"
    rule = Carrot(ver)
    assert not rule.get_is_match()

    ver = "^ 1.2.pre1"
    rule = Carrot(ver)
    assert not rule.get_is_match()

    ver = "^1.2.rc1"
    rule = Carrot(ver)
    assert not rule.get_is_match()

    ver = "^1.2.0"
    rule = Carrot(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    assert versions[0].prefix == ">="
    assert versions[0].major == 1
    assert versions[0].minor == 2
    assert versions[0].micro == 0

    assert versions[1].prefix == "<"
    assert versions[1].major == 2
    assert versions[1].minor == 0
    assert versions[1].micro == 0

    pip_ver_str = rule.get_versions_str()
    assert pip_ver_str == ">=1.2.0, <2.0.0"


@pytest.mark.parametrize(
    "ver,expect1,expect2",
    [
        pytest.param("^1.2.3", "1.2.3", "2.0.0", id="^1.2.3 low 1.2.3 hight 2.0.0"),
        pytest.param("^1.2", "1.2.0", "2.0.0", id="^1.2 low 1.2.0 hight 2.0.0"),
        pytest.param("^1", "1.0.0", "2.0.0", id="^1 low 1.0.0 hight 2.0.0"),
        pytest.param("^0.2.3", "0.2.3", "0.3.0", id="^0.2.3 low 0.2.3 hight 0.3.0"),
        pytest.param("^0.0.3", "0.0.3", "0.0.4", id="^0.0.3 low 0.0.3 hight 0.0.4"),
        pytest.param("^0.0", "0.0.0", "0.1.0", id="^0.0 low 0.0.0 hight 0.1.0"),
        pytest.param("^0", "0.0.0", "1.0.0", id="^0 low 0.0.0 hight 1.0.0"),
    ],
)
def test_get_version2(ver: str, expect1: str, expect2: str) -> None:
    # https://python-poetry.org/docs/dependency-specification/
    rule = Carrot(ver)
    assert rule.get_is_match()
    versions = rule.get_versions()
    assert len(versions) == 2
    v1 = versions[0]
    v2 = versions[1]
    assert str(v1) == expect1
    assert str(v2) == expect2
    v1_str = v1.get_pip_ver_str()
    expected_v1_str = f">={expect1}"
    assert v1_str == expected_v1_str
    v2_str = v2.get_pip_ver_str()
    expected_v2_str = f"<{expect2}"
    assert v2_str == expected_v2_str


def test_get_version_is_valid() -> None:
    ver = "^1.2.4"
    rule = Carrot(ver)
    assert rule.get_is_match()
    assert rule.get_version_is_valid("1.2.4") == 0
    assert rule.get_version_is_valid("1.2.5") == 0
    assert rule.get_version_is_valid("1.3.0") == 0
    assert rule.get_version_is_valid("2.0.0") == 1
    assert rule.get_version_is_valid("1.2.3") == -1


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "^1.2.4", 0),
        ("1.2.5", "^ 1.2.4", 0),
        ("1.2.5", "^1.2.3", 0),
        ("1.2.1", "^1.2.3", -1),
        ("2.0.0", "^1.2.3", 1),
        ("1.2.0", "^1.2", 0),
        ("1.1.9", "^1.2", -1),
        ("2.0.0", "^1.2", 1),
        ("1.1.0", "^1.2", -1),
        ("1.2.0", "^1", 0),
        ("0.2.0", "^1", -1),
        ("2.0.0", "^1", 1),
        ("0.2.3", "^0.2.3", 0),
        ("0.2.2", "^0.2.3", -1),
        ("0.3.0", "^0.2.3", 1),
        ("0.0.3", "^0.0.3", 0),
        ("0.0.2", "^0.0.3", -1),
        ("0.0.4", "^0.0.3", 1),
        ("0.0.3", "^0.0", 0),
        ("0.2.0", "^0.0", 1),
        ("0.9.0", "^0", 0),
        ("1.0.0", "^0", 1),
    ],
)
def test_get_version_is_valid_suffix(check_ver: str, vstr: str, result: int) -> None:
    rule = Carrot(vstr)
    assert rule.get_is_match()
    assert rule.get_version_is_valid(check_ver) == result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "^1.2.4", True),
        ("1.2.5", "^ 1.2.4", True),
        ("1.2.5", "^1.2.3", True),
        ("1.2.1", "^1.2.3", False),
        ("2.0.0", "^1.2.3", False),
        ("1.2.0", "^1.2", True),
        ("1.1.9", "^1.2", False),
        ("2.0.0", "^1.2", False),
        ("1.1.0", "^1.2", False),
        ("1.2.0", "^1", True),
        ("0.2.0", "^1", False),
        ("2.0.0", "^1", False),
        ("0.2.3", "^0.2.3", True),
        ("0.2.2", "^0.2.3", False),
        ("0.3.0", "^0.2.3", False),
        ("0.0.3", "^0.0.3", True),
        ("0.0.2", "^0.0.3", False),
        ("0.0.4", "^0.0.3", False),
        ("0.0.3", "^0.0", True),
        ("0.2.0", "^0.0", False),
        ("0.9.0", "^0", True),
        ("1.0.0", "^0", False),
    ],
)
def test_get_installed_valid(check_ver: str, vstr: str, result: bool) -> None:
    rule = Carrot(vstr)
    assert rule.get_is_match()
    assert rule.get_installed_is_valid(check_ver) == result
