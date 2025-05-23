from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_import_available import QryIsImportAvailable
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.general.qry_is_import_available import QryIsImportAvailable
    from ___lo_pip___.basic_config import BasicConfig


class QryIsImport2Available(QryBase, LogMixin, QryT[bool]):
    def __init__(self) -> None:
        """
        Initializes the instance.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cfg = BasicConfig()
        self.log.debug("init done")

    def _is_import_available(self, module_name: str) -> bool:
        """
        Checks if the module is available for import.

        Args:
            module_name (str): The name of the module to check for import availability.

        Returns:
            bool: True if the module is available for import, False otherwise.
        """
        qry = QryIsImportAvailable(module_name)
        return self._execute_qry(qry)

    def execute(self) -> bool:
        """
        Executes the query to get if imports are available that are listed in the configuration.

        Returns:
            bool: True if imports are available, False otherwise.
        """

        try:
            result = all(self._is_import_available(imp) for imp in self._cfg.run_imports2)
            self.log.debug("Import2 available: %s", result)
            return result
        except Exception:
            self.log.exception("Error getting script url")
        return False
