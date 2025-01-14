from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

from packaging.version import Version

from oxt.___lo_pip___.ver.req_version import ReqVersion


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "1.2.4", False),
        ("0.0.6", "0.0.3", True),
        ("0.0.3", "0.0.6", False),
        ("1.2.5", " 1.2.4", True),
        ("1.2.3", " 1.2.4", False),
        ("1.2rc1", "1.2.rc1", False),
        ("1.2rc2", "1.2.rc1", True),
        ("1.2dev3", "1.2.dev3", False),
        ("1.2dev1", "1.2dev2", False),
        ("1.2dev3", "1.2dev2", True),
        ("1.2post3", "1.2.post3", False),
        ("1.2post1", "1.2post2", False),
        ("1.2post3", "1.2post2", True),
    ],
)
def test_greater_than(check_ver: str, vstr: str, result: bool) -> None:
    # Python version convert pre to rc
    v1 = Version(check_ver)
    v2 = Version(vstr)
    assert (v1 > v2) is result

    installed_ver = ReqVersion(check_ver)
    req_ver = ReqVersion(vstr)
    assert (installed_ver > req_ver) is result
    assert (installed_ver > v2) is result
    assert (installed_ver > vstr) is result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "1.2.4", False),
        ("0.0.6", "0.0.3", False),
        ("0.0.3", "0.0.6", True),
        ("1.2.5", " 1.2.4", False),
        ("1.2.3", " 1.2.4", True),
        ("1.2rc1", "1.2.rc1", False),
        ("1.2rc2", "1.2.rc1", False),
        ("1.2dev3", "1.2.dev3", False),
        ("1.2dev1", "1.2dev2", True),
        ("1.2dev3", "1.2dev2", False),
        ("1.2post3", "1.2.post3", False),
        ("1.2post1", "1.2post2", True),
        ("1.2post3", "1.2post2", False),
    ],
)
def test_less_than(check_ver: str, vstr: str, result: bool) -> None:
    # Python version convert pre to rc
    v1 = Version(check_ver)
    v2 = Version(vstr)
    assert (v1 < v2) is result

    installed_ver = ReqVersion(check_ver)
    req_ver = ReqVersion(vstr)
    assert (installed_ver < req_ver) is result
    assert (installed_ver < v2) is result
    assert (installed_ver < vstr) is result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "1.2.4", True),
        ("0.0.6", "0.0.3", True),
        ("0.0.3", "0.0.6", False),
        ("1.2.5", " 1.2.4", True),
        ("1.2.3", " 1.2.4", False),
        ("1.2rc1", "1.2.rc1", True),
        ("1.2rc2", "1.2.rc1", True),
        ("1.2dev3", "1.2.dev3", True),
        ("1.2dev1", "1.2dev2", False),
        ("1.2dev3", "1.2dev2", True),
        ("1.2post3", "1.2.post3", True),
        ("1.2post1", "1.2post2", False),
        ("1.2post3", "1.2post2", True),
    ],
)
def test_greater_or_eq(check_ver: str, vstr: str, result: bool) -> None:
    # Python version convert pre to rc
    v1 = Version(check_ver)
    v2 = Version(vstr)
    assert (v1 >= v2) is result

    installed_ver = ReqVersion(check_ver)
    req_ver = ReqVersion(vstr)
    assert (installed_ver >= req_ver) is result
    assert (installed_ver >= v2) is result
    assert (installed_ver >= vstr) is result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "1.2.4", True),
        ("0.0.6", "0.0.3", False),
        ("0.0.3", "0.0.6", True),
        ("1.2.5", " 1.2.4", False),
        ("1.2.3", " 1.2.4", True),
        ("1.2rc1", "1.2.rc1", True),
        ("1.2rc2", "1.2.rc1", False),
        ("1.2dev3", "1.2.dev3", True),
        ("1.2dev1", "1.2dev2", True),
        ("1.2dev3", "1.2dev2", False),
        ("1.2post3", "1.2.post3", True),
        ("1.2post1", "1.2post2", True),
        ("1.2post3", "1.2post2", False),
    ],
)
def test_less_or_eq(check_ver: str, vstr: str, result: bool) -> None:
    # Python version convert pre to rc
    v1 = Version(check_ver)
    v2 = Version(vstr)
    assert (v1 <= v2) is result

    installed_ver = ReqVersion(check_ver)
    req_ver = ReqVersion(vstr)
    assert (installed_ver <= req_ver) is result
    assert (installed_ver <= v2) is result
    assert (installed_ver <= vstr) is result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "1.2.4", True),
        ("0.0.6", "0.0.3", False),
        ("0.0.3", "0.0.6", False),
        ("1.2.5", " 1.2.5", True),
        ("1.2.3", " 1.2.4", False),
        ("1.2rc1", "1.2.rc1", True),
        ("1.2rc2", "1.2.rc1", False),
        ("1.2dev3", "1.2.dev3", True),
        ("1.2dev1", "1.2dev2", False),
        ("1.2dev3", "1.2dev2", False),
        ("1.2post3", "1.2.post3", True),
        ("1.2post1", "1.2post2", False),
        ("1.2post3", "1.2post2", False),
    ],
)
def test_eq(check_ver: str, vstr: str, result: bool) -> None:
    # Python version convert pre to rc
    v1 = Version(check_ver)
    v2 = Version(vstr)
    assert (v1 == v2) is result

    installed_ver = ReqVersion(check_ver)
    req_ver = ReqVersion(vstr)
    assert (installed_ver == req_ver) is result
    assert (installed_ver == v2) is result
    assert (installed_ver == vstr) is result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "1.2.4", False),
        ("0.0.6", "0.0.3", True),
        ("0.0.3", "0.0.6", True),
        ("1.2.5", " 1.2.5", False),
        ("1.2.3", " 1.2.4", True),
        ("1.2rc1", "1.2.rc1", False),
        ("1.2rc2", "1.2.rc1", True),
        ("1.2dev3", "1.2.dev3", False),
        ("1.2dev1", "1.2dev2", True),
        ("1.2dev3", "1.2dev2", True),
        ("1.2post3", "1.2.post3", False),
        ("1.2post1", "1.2post2", True),
        ("1.2post3", "1.2post2", True),
    ],
)
def test_not_eq(check_ver: str, vstr: str, result: bool) -> None:
    # Python version convert pre to rc
    v1 = Version(check_ver)
    v2 = Version(vstr)
    assert (v1 != v2) is result

    installed_ver = ReqVersion(check_ver)
    req_ver = ReqVersion(vstr)
    assert (installed_ver != req_ver) is result
    assert (installed_ver != v2) is result
    assert (installed_ver != vstr) is result
