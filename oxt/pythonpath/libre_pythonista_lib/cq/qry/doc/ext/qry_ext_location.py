from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.___lo_pip___.config import Config
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from ___lo_pip___.config import Config
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT


class QryExtLocation(QryBase, LogMixin, QryT[str]):
    """Gets the location for the extension. Either ``share`` or ``user``"""

    def __init__(self) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.log.debug("init done")

    def _get_config(self) -> Config:
        # for testing
        return Config()

    def execute(self) -> str:
        """
        Executes the query and returns the location.

        Returns:
            str: Location for the extension. Either ``share`` or ``user``.
        """
        try:
            config = self._get_config()
            location = "share" if config.is_shared_installed else "user"
            return location
        except Exception:
            self.log.exception("Error executing query")
        return ""
