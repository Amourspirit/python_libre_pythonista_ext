from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from ___lo_pip___.basic_config import BasicConfig


# tested in: tests/test_cmd/test_cmd_sheet_ensure_forms.py


class QryFormName(QryBase, QryT[str]):
    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> str:
        """
        Executes the query and returns the form name.

        The form name is built from the general code name.

        Returns:
            str: The form name.
        """
        config = BasicConfig()
        return f"Form_{config.general_code_name}"
