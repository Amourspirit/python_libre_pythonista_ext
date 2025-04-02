from __future__ import annotations
from typing import Any, Dict, Protocol

from ooodev.utils.helper.dot_dict import DotDict


class PyModuleT(Protocol):
    def copy_dict(self) -> Dict[str, Any]:
        """Returns a copy of the module dictionary."""
        ...

    def execute_code(self, code_snippet: str, globals: dict | None = None) -> Any:  # noqa: ANN401
        """
        Compiles and executes the given code snippet.
        - If the last statement is an expression, returns its value.
        - Otherwise, returns the value of `result` if it exists in local variables.
        """
        ...

    def reset_module(self) -> None:
        """Reset the module to its initial state."""
        ...

    def update_with_result(self, code: str = "") -> DotDict[Any]:
        """
        Appends code to current module and returns the last variable in the module.

        Args:
            code (str, optional): Any valid python code

        Returns:
            Any: The last variable in the module if any; Otherwise, None.

        Note:
            If there is an error the result will be a DotDict with ``data=GeneralError(e)`` and ``error=True`` the error.
        """
        ...

    def set_global_var(self, var_name: str, value: Any) -> None:  # noqa: ANN401
        """
        Set a global variable in the module.

        Args:
            var_name (str): The name of the variable
            value (Any): The value of the variable
        """
        ...

    def reset_to_dict(self, mod_dict: Dict[str, Any], code: str = "") -> Any:  # noqa: ANN401
        """
        Reset the module to the given dictionary and returns the last variable in the module if code is present.

        Args:
            mod_dict (dict): A dictionary of variables to reset the module to.
            code (str, optional): Any valid python code

        Returns:
            Any: If there is code the last variable in the module if any; Otherwise, None.
        """
        ...
