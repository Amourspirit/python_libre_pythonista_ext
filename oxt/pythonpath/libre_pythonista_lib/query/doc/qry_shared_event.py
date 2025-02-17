from __future__ import annotations


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.qry_t import QryT


class QrySharedEvent(LogMixin, QryT):
    def __init__(self) -> None:
        LogMixin.__init__(self)

    def execute(self) -> SharedEvent | None:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        try:
            return SharedEvent()
        except Exception:
            self.log.exception("Error getting script url")
        return None
