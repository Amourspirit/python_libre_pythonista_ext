import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def test_req_ver():
    from oxt.___lo_pip___.ver.req_version import ReqVersion

    ver = ReqVersion("==1.0.0")
    assert ver.get_pip_ver_str() == "==1.0.0"
    assert ver.version_parts.has_minor
    assert ver.version_parts.has_micro

    ver = ReqVersion("==1.2")
    assert ver.version_parts.has_minor
    assert ver.version_parts.has_micro is False

    ver = ReqVersion("==1")
    assert ver.version_parts.has_minor is False
    assert ver.version_parts.has_micro is False
