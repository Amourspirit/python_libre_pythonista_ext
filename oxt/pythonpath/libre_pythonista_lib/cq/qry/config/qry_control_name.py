from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT


class QryControlName(QryBase, QryT[str]):
    """
    Query that generates a control name based on a code name.
    Inherits from QryBase and implements QryT[str].
    """

    def __init__(self, code_name: str) -> None:
        """
        Initialize the query with a code name.

        Args:
            code_name (str): The code identifier to use in the control name
        """
        QryBase.__init__(self)
        self._code_name = code_name
        self._config = BasicConfig()

    def _get_control_name(self, code_name: str) -> str:
        """
        Generates a control name by combining the general code name from config with the provided code name.

        Args:
            code_name (str): The code identifier to use in the control name

        Returns:
            str: The generated control name in format: {general_code_name}_ctl_cell_{code_name}
        """
        return f"{self._config.general_code_name}_ctl_cell_{code_name}"

    def execute(self) -> str:
        """
        Executes the query to generate the control name.

        Returns:
            str: The generated control name
        """
        return self._get_control_name(self._code_name)
