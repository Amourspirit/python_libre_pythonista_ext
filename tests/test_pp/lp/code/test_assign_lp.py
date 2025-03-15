from __future__ import annotations
from typing import Any, TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule


def test_lp_cell(py_mod: PyModule) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign
    else:
        from libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign

    py_mod.mod.__dict__["lp"] = lambda x: 3
    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=3)
    code = """
result = lp("A1")
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert result.data == 3

    code = """
result = lp(
    "A1"
)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert result.data == 3


def test_lp_range(py_mod: PyModule) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign
    else:
        from libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign

    py_mod.mod.__dict__["lp"] = lambda x: 3
    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=3, headers=False)
    code = """
result = lp("A1:C3")
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert result.data == 3

    code = """
result = lp(
    "A1:C3"
)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert result.data == 3


def test_lp_range_headers(py_mod: PyModule) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign
    else:
        from libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign

    def lp(x, headers=False) -> int:  # noqa: ANN001
        return 3

    py_mod.mod.__dict__["lp"] = lp
    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=3, headers=False)
    code = """
result = lp("A1:C3", headers=True)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert result.data == 3

    code = """

# This is a comment
result = lp(
    "A1:C3", # this is a comment
    headers=True
)

"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert result.data == 3


# df:pd.DataFrame = lp("A2:D13", headers=True)


def test_lp_df(py_mod: PyModule, import_available) -> None:  # noqa: ANN001
    if not import_available("pandas"):
        pytest.skip("Skipping this test because pandas in not installed.")

    from ooodev.utils.helper.dot_dict import DotDict
    import pandas as pd

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign
    else:
        from libre_pythonista_lib.code.rules.lp_fn_assign import LpFnAssign

    def lp(x, headers=True) -> Any:  # noqa: ANN001, ANN401
        # return a pandas DataFrame
        return pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

    py_mod.mod.__dict__["lp"] = lp
    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=lp(None), headers=True)
    code = """
result = lp("A1:C3", headers=True)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert isinstance(result.data, pd.DataFrame)

    code = """

# This is a comment
df:pd.DataFrame = lp(
    "A1:C3", # this is a comment
    headers=True
)

"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnAssign)
    assert result is not None
    assert isinstance(result.data, pd.DataFrame)
