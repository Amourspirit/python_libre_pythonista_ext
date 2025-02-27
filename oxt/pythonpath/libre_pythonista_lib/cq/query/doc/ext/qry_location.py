from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.___lo_pip___.config import Config
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from ___lo_pip___.config import Config
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryLocation(QryBase, LogMixin, QryT[str]):
    def __init__(self) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SIMPLE

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
