from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])


from oxt.___lo_pip___.ver.rules.ver_rules import VerRules
from oxt.___lo_pip___.ver.req_version import ReqVersion


@pytest.mark.parametrize(
    "vstr,gstr,valid_str",
    [
        ("==1.2.3", "==1.2.3", "1.2.3"),
        ("==1.2rc1", "==1.2rc1", "1.2rc1"),
        (">1.2.3", ">1.2.3", "1.2.4"),
        ("<1.2.3", "<1.2.3", "1.2.2"),
        (">=1.2.3", ">=1.2.3", "1.2.4"),
        ("<=1.2.3", "<=1.2.3", "1.2.3"),
        ("!=1.2.3", "!=1.2.3", "1.2"),
        ("<> 1.2.3", "!=1.2.3", "2.2"),
        ("^1.2", ">=1.2, <2.0.0", "1.5"),
        ("~=1.2", ">=1.2, <1.3.0", "1.2.4"),
        ("==2.*", ">=2, <3.0.0", "2.2.4"),
        ("== 1.2.3", "==1.2.3", "1.2.3"),
        ("> 1.2.3", ">1.2.3", "1.2.4"),
        ("< 1.2.3", "<1.2.3", "1.2.2"),
        (">= 1.2.3", ">=1.2.3", "1.2.4"),
        ("<= 1.2.3", "<=1.2.3", "1.2.3"),
        ("!= 1.2.3", "!=1.2.3", "1.2"),
        ("^ 1.2", ">=1.2, <2.0.0", "1.5"),
        ("~= 1.2", ">=1.2, <1.3.0", "1.2.4"),
    ],
)
def test_rules(vstr: str, gstr: str, valid_str: str) -> None:
    vr = VerRules()
    rules = vr.get_matched_rules(vstr)
    assert len(rules) == 1
    rule = rules[0]
    assert rule.get_versions_str() == gstr
    assert rule.get_version_is_valid(valid_str) == 0


def test_rules_multi() -> None:
    from packaging.version import Version

    vr = VerRules()
    installed_ver = "1.1.3"
    vstr = ">=1.2"
    rules = vr.get_matched_rules(vstr)
    assert len(rules) == 1
    rule = rules[0]
    # installed version is not valid and new version should be installed
    assert rule.get_version_is_valid(installed_ver) != 0

    installed_ver = "3.1"
    # installed version is valid and new version should not be installed
    assert rule.get_version_is_valid(installed_ver) == 0

    vstr = ">=1.2.3,<2.0.0"
    rules = vr.get_matched_rules(vstr)


@pytest.mark.parametrize(
    "installed_str,vstr",
    [
        ("1.2.4", "<=1.2.3"),
        ("2.4", "^1.2.3"),
        ("1.3.4", "==1.2.*"),
        ("1.3", "<1.2"),
        ("1.3", "==1.2"),
    ],
)
def test_expect_fail_due_to_high_ver_installed(installed_str: str, vstr: str) -> None:
    vr = VerRules()
    rules = vr.get_matched_rules(vstr)
    assert len(rules) >= 1
    for rule in rules:
        assert rule.get_version_is_valid(installed_str) != 0


@pytest.mark.parametrize(
    "installed_str,vstr",
    [
        ("1.2.5", ">=1.2.3, >=1.2.5"),
        ("1.2.4", "^1.2"),
        ("1.2.6", ">1.2.3, >1.2.5"),
        ("1.2.6", "==1.2.*, >1.2.5"),
        ("1.2.99", "==1.2.*"),
        ("1.2.6", ">=1.2.1, >1.2.2, >1.2.3, >1.2.4, >1.2.5"),
    ],
)
def test_expect_pass_compound_rule(installed_str: str, vstr: str) -> None:
    # compound rules are 'and' rules, so all rules must be true
    vr = VerRules()
    rules = vr.get_matched_rules(vstr)
    assert len(rules) >= 1
    result = True
    for rule in rules:
        result = result and rule.get_version_is_valid(installed_str) == 0
        if result == False:
            break
    assert result == True


@pytest.mark.parametrize(
    "installed_str,vstr",
    [
        ("1.2.4", "<=1.2.3, >=1.2.5"),
        ("2.0", "^1.2"),
        ("1.2.4", "<1.2.3, >1.2.5"),
        ("1.3", "==1.2.*"),
        ("1.2.7", "<=1.2.3, >=1.2.6"),
        ("1.2.7", ">=1.2.1, >1.2.2, >1.2.3, >1.2.4, >1.2.5, <1.2.7"),
    ],
)
def test_expect_fail_compound_rule(installed_str: str, vstr: str) -> None:
    # compound rules are 'and' rules, so all rules must be true to pass or any rule false to fail all
    vr = VerRules()
    rules = vr.get_matched_rules(vstr)
    assert len(rules) >= 1
    result = True
    for rule in rules:
        result = result and rule.get_version_is_valid(installed_str) == 0
        if result == False:
            break
    assert result == False


@pytest.mark.parametrize(
    "installed_str,vstr,expected_result",
    [
        ("1.2.4", "!=1.2.3", True),
        ("1.2.3", "!=1.2.3", False),
        ("1.2.3", "!=1.2.3, >1.2.4", False),
    ],
)
def test_expect_not_equal(installed_str: str, vstr: str, expected_result: bool) -> None:
    vr = VerRules()
    rules = vr.get_matched_rules(vstr)
    assert len(rules) >= 1
    for rule in rules:
        result = rule.get_version_is_valid(installed_str) == 0
        assert result == expected_result


@pytest.mark.parametrize(
    "check_ver,vstr,result",
    [
        ("1.2.4", "^1.2.4", True),
        ("1.2.5", "^1.2.4", True),
        ("1.2.3", "^1.2.4", False),
        ("1.1.1", "!=1.1.0, ^1.2.4", False),
        ("1.3.3", "!=1.1.0, ^1.2.4", True),
        ("1.1.0", "!=1.1.0, ^1.0.4", False),
        ("1.1.1", "!=1.1.0, >=1.0.9", True),
        ("1.1.4", "<1.1.5, >1.1.3", True),
        ("1.1.6", "<1.1.5, >1.1.3", False),
        ("1.1.4", "<1.1.5, >1.1.3", True),
        ("1.1.2", "<1.1.5, >1.1.1", True),
        ("1.1.2", "<1.1.5, >1.1.1, !=1.1.2", False),
        ("1.1.5", ">=1.1.5, <=1.1.5", True),
        ("1.5.2", ">=1.5, >1.1.5", True),
        ("1.5.2", ">=1.5, <2", True),
        ("1.4.2", ">=1.5, <2", False),
        ("2.1", ">=1.5, <2", False),
        ("1.5", ">=1.5, <2", True),
        ("5", ">=1.5, <2", False),
        ("1.999", ">=1.5, <2", True),
        ("1.5.2", "~=1.5", True),
        ("1.5.99", "~=1.5", True),
        ("1.6.0", "~=1.5", False),
        ("1.7", "~=1.5", False),
        ("1.5.2", "~=1.5, <2", True),
        ("1.5.2", "~=1.5, <2, !=1.5.1", True),
        ("1.5.2", "~=1.5, <2, !=1.5.2", False),
        ("1.6.0", "==1.*", True),
        ("1.6.0", "==1.*, !=1.6.0", False),
        ("2.0", "==1.*", False),
        ("1.1.2", "^1.1.2", True),
    ],
)
def test_meet_requirements(check_ver: str, vstr: str, result: bool) -> None:
    vr = VerRules()
    assert vr.get_installed_is_valid(vstr=vstr, check_version=check_ver) == result
