from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install import QryIsSharedInstall
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.general.qry_is_shared_install import QryIsSharedInstall


class QryLocation(QryBase, QryT[str]):
    """Gets the location for the extension. Either ``share:uno_packages`` or ``user:uno_packages``"""

    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> str:
        """
        Executes the query and returns the location.

        Returns:
            str: Location for the extension. Either ``share:uno_packages`` or ``user:uno_packages``.
        """
        qry = QryIsSharedInstall()
        is_shared = self._execute_qry(qry)
        return "share:uno_packages" if is_shared else "user:uno_packages"
