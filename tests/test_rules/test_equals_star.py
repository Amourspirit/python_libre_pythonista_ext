from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.equals_star import EqualsStar


@pytest.mark.parametrize(
    "match",
    [
        ("==1.0.0.*"),
        ("== 1.0.*"),
        ("==  1.*"),
        ("==0.0.1.*"),
    ],
)
def test_is_match(match: str) -> None:
    rule = EqualsStar(match)
    assert rule.get_is_match()


@pytest.mark.parametrize(
    "match",
    [
        ("!=1.0.*"),
        ("~=1.*"),
        ("!=1.0"),
        ("~=1"),
        ("*=0.0.1"),
    ],
)
def test_is_not_match(match: str) -> None:
    rule = EqualsStar(match)
    assert rule.get_is_match() is False


@pytest.mark.parametrize(
    "check_ver,vstr",
    [
        ("==1.2.4.*", ">=1.2.4, <1.2.5.dev1"),
        ("==1.2.*", ">=1.2, <1.3.dev1"),
        ("==1.*", ">=1, <2.dev1"),
    ],
)
def test_check_version_str(check_ver: str, vstr: str) -> None:
    rule = EqualsStar(check_ver)
    assert rule.get_is_match()
    vers = rule.get_versions()
    v1 = vers[0]
    v2 = vers[1]
    v_str = f"{v1.get_pip_ver_str()}, {v2.get_pip_ver_str()}"
    assert v_str == vstr


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "==1.2.4.*", 0),
        ("1.2.4.post1", "==1.2.4.*", 0),
        ("1.2.4.post7", "==1.2.4.*", 0),
        ("1.2.4.a1", "==1.2.4.*", -1),
        ("1.2.4.rc1", "==1.2.4.*", -1),
        ("1.2.5.dev1", "==1.2.4.*", 1),
        ("1.2.5", "==1.2.4.*", 1),
        ("1.2", "==1.2.*", 0),
        ("1.2.1", "==1.2.*", 0),
        ("1.2.1.post1", "==1.2.*", 0),
        ("1.3", "==1.2.*", 1),
        ("1.3.dev1", "==1.2.*", 1),
        ("1", "==1.*", 0),
        ("1.1.1", "==1.*", 0),
        ("1.1.1.post1", "==1.*", 0),
        ("2.dev1", "==1.*", 1),
        ("1rc1", "==1.*", -1),
        ("1a1", "==1.*", -1),
        ("2rc1", "==1.*", 1),
        ("1.post1", "==1.*", 0),
        ("1.0.1", "==1.*", 0),
        ("1.0.1.post1", "==1.*", 0),
        ("1.1", "==1.*", 0),
        ("1.1.post1", "==1.*", 0),
        ("1.1.1", "==1.*", 0),
        ("1.1.1.post1", "==1.*", 0),
    ],
)
def test_get_version_is_valid_suffix(check_ver: str, vstr: str, result: int) -> None:
    rule = EqualsStar(vstr)
    assert rule.get_is_match()
    assert rule.get_version_is_valid(check_ver) == result
