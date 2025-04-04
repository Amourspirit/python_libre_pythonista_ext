from __future__ import annotations


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_t import QryT


class QrySharedEvent(QryBase, LogMixin, QryT[SharedEvent | None]):
    def __init__(self) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.log.debug("init done")

    def execute(self) -> SharedEvent | None:
        """
        Executes the query to get the shared event.

        Returns:
            SharedEvent: The shared event or None if an error occurred.
        """

        try:
            return SharedEvent()
        except Exception:
            self.log.exception("Error getting script url")
        return None
