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

# tested in tests/test_cmd_qry/test_doc/ext/test_qry_location.py
# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_version.py


class QryExtVersion(QryBase, QryT[str]):
    """Gets the lp version from the configuration"""

    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> str:
        """
        Executes the query and returns the lp version from the configuration.

        Returns:
            str: The lp version from the configuration.
        """
        return BasicConfig().extension_version
