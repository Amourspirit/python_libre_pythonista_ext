from __future__ import annotations
from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT


class QrySheetScriptUrl(QryBase, LogMixin, QryT[Union[str, None]]):
    def __init__(self) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.log.debug("init done")

    def execute(self) -> Union[str, None]:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str, None: The script URL if successful, otherwise None.
        """

        try:
            return calculate.get_script_url()
        except Exception:
            self.log.exception("Error getting script url")
        return None
