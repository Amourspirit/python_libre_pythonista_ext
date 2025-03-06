from __future__ import annotations


import importlib.util
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT


class QryIsImportAvailable(QryBase, LogMixin, QryT[bool]):
    def __init__(self, module_name: str) -> None:
        """
        Initializes the instance.

        Args:
            module_name (str): The name of the module to check for import availability.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._module_name = module_name

    def execute(self) -> bool:
        """
        Executes the query to get if import is available.

        Returns:
            bool: True if import is available, False otherwise.
        """

        try:
            spec = importlib.util.find_spec(self._module_name)
            result = spec is not None
            self.log.debug("Import available: %s", result)
            return result
        except Exception:
            self.log.exception("Error getting script url")
        return False
