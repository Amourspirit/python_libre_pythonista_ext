from __future__ import annotations


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.___lo_pip___.config import Config
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from ___lo_pip___.config import Config


class QryIsSharedInstall(QryBase, QryT[bool]):
    """Checks if the extension is installed in the shared location."""

    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> bool:
        """
        Executes the query and returns if the extension is installed in the shared location.

        Returns:
            bool: True if the extension is installed in the shared location, False otherwise.
        """
        return Config().is_shared_installed
