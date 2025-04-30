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


class QryCellCpCodeName(QryBase, QryT[str]):
    """
    Query class that retrieves the codename from configuration.
    Something like ``libre_pythonista_codename``

    This class inherits from QryBase and implements QryT[str] to provide
    type-safe query functionality for retrieving the cell copy codename.
    """

    def __init__(self) -> None:
        """
        Initialize the query.
        """
        QryBase.__init__(self)

    def execute(self) -> str:
        """
        Execute the query to get the codename.
        Something like ``libre_pythonista_codename``

        Returns:
            str: The configured codename.
        """
        return BasicConfig().cell_cp_codename
